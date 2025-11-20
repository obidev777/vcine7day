from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
import json
import os
from datetime import datetime
import uuid
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'vc7day_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Archivo JSON para almacenar datos
DATA_FILE = 'data.json'

# Inicializar datos si no existen
def init_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "categories": [
                {"id": 1, "name": "Música", "icon": "🎵", "created_at": datetime.now().isoformat()},
                {"id": 2, "name": "Gaming", "icon": "🎮", "created_at": datetime.now().isoformat()},
                {"id": 3, "name": "Educación", "icon": "📚", "created_at": datetime.now().isoformat()},
                {"id": 4, "name": "Tecnología", "icon": "💻", "created_at": datetime.now().isoformat()},
                {"id": 5, "name": "Deportes", "icon": "⚽", "created_at": datetime.now().isoformat()}
            ],
            "playlists": [
                {
                    "id": 1,
                    "name": "Tutoriales de Python",
                    "description": "Aprende Python desde cero hasta avanzado",
                    "category_id": 3,
                    "videos": [1, 3],
                    "thumbnail": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerBlazes.jpg",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "name": "Música Relajante",
                    "description": "Las mejores melodías para estudiar y relajarse",
                    "category_id": 1,
                    "videos": [2],
                    "thumbnail": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ElephantsDream.jpg",
                    "created_at": datetime.now().isoformat()
                }
            ],
            "videos": [
                {
                    "id": 1,
                    "title": "Bienvenido a VC7Day - La mejor plataforma de videos online para toda la familia",
                    "description": "La mejor plataforma de videos online con contenido variado y de calidad para todos los gustos",
                    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                    "thumbnail": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg",
                    "category_id": 3,
                    "playlist_id": 1,
                    "views": 150,
                    "likes": 45,
                    "related_videos": [2, 3],
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "title": "Música Relajante - Las mejores melodías para relajarse después del trabajo",
                    "description": "Las mejores melodías para relajarse y meditar. Perfecto para momentos de tranquilidad.",
                    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                    "thumbnail": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ElephantsDream.jpg",
                    "category_id": 1,
                    "playlist_id": 2,
                    "views": 89,
                    "likes": 23,
                    "related_videos": [1],
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": 3,
                    "title": "Tutorial de Python Completo - Aprende Python desde cero hasta nivel avanzado",
                    "description": "Aprende Python desde cero con este tutorial completo que cubre todos los aspectos del lenguaje",
                    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                    "thumbnail": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerBlazes.jpg",
                    "category_id": 4,
                    "playlist_id": 1,
                    "views": 234,
                    "likes": 67,
                    "related_videos": [1, 2],
                    "created_at": datetime.now().isoformat()
                }
            ],
            "settings": {
                "related_videos_count": 6,
                "auto_related": True,
                "default_related_strategy": "category"
            }
        }
        save_data(default_data)

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"categories": [], "playlists": [], "videos": [], "settings": {
            "related_videos_count": 6,
            "auto_related": True,
            "default_related_strategy": "category"
        }}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Middleware para verificar autenticación
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Funciones auxiliares
def get_category_name(category_id, categories):
    category = next((c for c in categories if c['id'] == category_id), None)
    return category['name'] if category else 'Sin categoría'

def get_playlist_name(playlist_id, playlists):
    playlist = next((p for p in playlists if p['id'] == playlist_id), None)
    return playlist['name'] if playlist else 'Sin playlist'

# Rutas principales
@app.route('/')
def index():
    data = load_data()
    categories = data.get('categories', [])
    videos = data.get('videos', [])
    playlists = data.get('playlists', [])
    
    # Ordenar videos por fecha de creación (más recientes primero)
    videos.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template('index.html', 
                         categories=categories, 
                         videos=videos,
                         playlists=playlists)

@app.route('/category/<int:category_id>')
def category_videos(category_id):
    data = load_data()
    categories = data.get('categories', [])
    videos = data.get('videos', [])
    playlists = data.get('playlists', [])
    
    category_videos = [v for v in videos if v['category_id'] == category_id]
    category_playlists = [p for p in playlists if p['category_id'] == category_id]
    category = next((c for c in categories if c['id'] == category_id), None)
    
    return render_template('category.html', 
                         categories=categories,
                         videos=category_videos,
                         playlists=category_playlists,
                         current_category=category)

@app.route('/playlist/<int:playlist_id>')
def playlist_videos(playlist_id):
    data = load_data()
    categories = data.get('categories', [])
    videos = data.get('videos', [])
    playlists = data.get('playlists', [])
    
    playlist = next((p for p in playlists if p['id'] == playlist_id), None)
    if not playlist:
        return "Playlist no encontrada", 404
    
    playlist_videos = [v for v in videos if v['id'] in playlist.get('videos', [])]
    category = next((c for c in categories if c['id'] == playlist['category_id']), None)
    
    return render_template('playlist.html', 
                         categories=categories,
                         videos=playlist_videos,
                         playlist=playlist,
                         category=category)

@app.route('/video/<int:video_id>')
def watch_video(video_id):
    data = load_data()
    videos = data.get('videos', [])
    categories = data.get('categories', [])
    playlists = data.get('playlists', [])
    settings = data.get('settings', {})
    
    video = next((v for v in videos if v['id'] == video_id), None)
    if not video:
        return "Video no encontrado", 404
    
    # Incrementar vistas
    video['views'] = video.get('views', 0) + 1
    save_data(data)
    
    # Obtener videos relacionados
    related_videos = get_related_videos(video, videos, settings)
    
    # Obtener categoría del video
    video_category = next((c for c in categories if c['id'] == video['category_id']), None)
    
    # Obtener playlist del video si existe
    video_playlist = None
    if video.get('playlist_id'):
        video_playlist = next((p for p in playlists if p['id'] == video['playlist_id']), None)
    
    return render_template('watch.html', 
                         video=video,
                         video_category=video_category,
                         video_playlist=video_playlist,
                         categories=categories,
                         related_videos=related_videos)

def get_related_videos(current_video, all_videos, settings):
    """Obtiene videos relacionados basado en la configuración"""
    related_videos = []
    
    # Primero usar videos relacionados configurados manualmente
    manual_related = current_video.get('related_videos', [])
    if manual_related:
        for video_id in manual_related:
            related_video = next((v for v in all_videos if v['id'] == video_id), None)
            if related_video and related_video['id'] != current_video['id']:
                related_videos.append(related_video)
    
    # Si no hay suficientes videos relacionados y auto_related está activado
    max_related = settings.get('related_videos_count', 6)
    if settings.get('auto_related', True) and len(related_videos) < max_related:
        strategy = settings.get('default_related_strategy', 'category')
        
        if strategy == 'category':
            # Videos de la misma categoría
            category_related = [v for v in all_videos 
                              if v['category_id'] == current_video['category_id'] 
                              and v['id'] != current_video['id']
                              and v not in related_videos]
            related_videos.extend(category_related)
        
        elif strategy == 'recent':
            # Videos más recientes
            recent_related = [v for v in all_videos 
                            if v['id'] != current_video['id'] 
                            and v not in related_videos]
            recent_related.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            related_videos.extend(recent_related)
        
        elif strategy == 'popular':
            # Videos más populares
            popular_related = [v for v in all_videos 
                             if v['id'] != current_video['id'] 
                             and v not in related_videos]
            popular_related.sort(key=lambda x: x.get('views', 0), reverse=True)
            related_videos.extend(popular_related)
    
    # Limitar al número máximo configurado y eliminar duplicados
    seen_ids = set()
    unique_related = []
    for video in related_videos:
        if video['id'] not in seen_ids and len(unique_related) < max_related:
            seen_ids.add(video['id'])
            unique_related.append(video)
    
    return unique_related

@app.route('/search')
def search():
    query = request.args.get('q', '')
    data = load_data()
    categories = data.get('categories', [])
    videos = data.get('videos', [])
    playlists = data.get('playlists', [])
    
    if query:
        search_videos = [v for v in videos if query.lower() in v['title'].lower() or query.lower() in v['description'].lower()]
        search_playlists = [p for p in playlists if query.lower() in p['name'].lower() or query.lower() in p['description'].lower()]
    else:
        search_videos = []
        search_playlists = []
    
    return render_template('search.html',
                         categories=categories,
                         videos=search_videos,
                         playlists=search_playlists,
                         search_query=query)

# Sistema de administración
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'obi123':
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Contraseña incorrecta')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    data = load_data()
    return render_template('admin_dashboard.html', 
                         categories=data.get('categories', []),
                         videos=data.get('videos', []),
                         playlists=data.get('playlists', []),
                         settings=data.get('settings', {}))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    data = load_data()
    
    if request.method == 'POST':
        settings = data.get('settings', {})
        settings['related_videos_count'] = int(request.form.get('related_videos_count', 6))
        settings['auto_related'] = 'auto_related' in request.form
        settings['default_related_strategy'] = request.form.get('default_related_strategy', 'category')
        
        data['settings'] = settings
        save_data(data)
        return redirect(url_for('admin_settings'))
    
    return render_template('admin_settings.html', 
                         settings=data.get('settings', {}))

@app.route('/admin/categories')
@login_required
def admin_categories():
    data = load_data()
    return render_template('admin_categories.html', categories=data.get('categories', []))

@app.route('/admin/categories/add', methods=['POST'])
@login_required
def add_category():
    data = load_data()
    categories = data.get('categories', [])
    
    new_category = {
        "id": max([c['id'] for c in categories], default=0) + 1,
        "name": request.form.get('name'),
        "icon": request.form.get('icon'),
        "created_at": datetime.now().isoformat()
    }
    
    categories.append(new_category)
    data['categories'] = categories
    save_data(data)
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/delete/<int:category_id>')
@login_required
def delete_category(category_id):
    data = load_data()
    categories = data.get('categories', [])
    
    # Verificar si hay videos en esta categoría
    videos_in_category = [v for v in data.get('videos', []) if v['category_id'] == category_id]
    if videos_in_category:
        return "No se puede eliminar la categoría porque tiene videos asociados", 400
    
    data['categories'] = [c for c in categories if c['id'] != category_id]
    save_data(data)
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/playlists')
@login_required
def admin_playlists():
    data = load_data()
    playlists = data.get('playlists', [])
    categories = data.get('categories', [])
    videos = data.get('videos', [])
    
    # Agregar información adicional a las playlists
    for playlist in playlists:
        playlist['category_name'] = get_category_name(playlist['category_id'], categories)
        playlist['videos_count'] = len(playlist.get('videos', []))
        if playlist.get('videos'):
            playlist['first_video'] = next((v for v in videos if v['id'] == playlist['videos'][0]), None)
    
    return render_template('admin_playlists.html', 
                         playlists=playlists, 
                         categories=categories,
                         videos=videos)

@app.route('/admin/playlists/add', methods=['POST'])
@login_required
def add_playlist():
    data = load_data()
    playlists = data.get('playlists', [])
    
    # Procesar videos de la playlist
    videos_input = request.form.get('videos', '')
    playlist_videos = []
    if videos_input:
        try:
            playlist_videos = [int(x.strip()) for x in videos_input.split(',') if x.strip().isdigit()]
        except:
            playlist_videos = []
    
    new_playlist = {
        "id": max([p['id'] for p in playlists], default=0) + 1,
        "name": request.form.get('name'),
        "description": request.form.get('description'),
        "category_id": int(request.form.get('category_id')),
        "videos": playlist_videos,
        "thumbnail": request.form.get('thumbnail'),
        "created_at": datetime.now().isoformat()
    }
    
    playlists.append(new_playlist)
    data['playlists'] = playlists
    save_data(data)
    
    return redirect(url_for('admin_playlists'))

@app.route('/admin/playlists/edit/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def edit_playlist(playlist_id):
    data = load_data()
    playlists = data.get('playlists', [])
    categories = data.get('categories', [])
    videos = data.get('videos', [])
    
    playlist = next((p for p in playlists if p['id'] == playlist_id), None)
    if not playlist:
        return "Playlist no encontrada", 404
    
    if request.method == 'POST':
        # Procesar videos de la playlist
        videos_input = request.form.get('videos', '')
        playlist_videos = []
        if videos_input:
            try:
                playlist_videos = [int(x.strip()) for x in videos_input.split(',') if x.strip().isdigit()]
            except:
                playlist_videos = []
        
        playlist['name'] = request.form.get('name')
        playlist['description'] = request.form.get('description')
        playlist['category_id'] = int(request.form.get('category_id'))
        playlist['thumbnail'] = request.form.get('thumbnail')
        playlist['videos'] = playlist_videos
        
        save_data(data)
        return redirect(url_for('admin_playlists'))
    
    # Obtener información de videos de la playlist
    playlist_videos_info = []
    for video_id in playlist.get('videos', []):
        video = next((v for v in videos if v['id'] == video_id), None)
        if video:
            playlist_videos_info.append(video)
    
    return render_template('admin_edit_playlist.html', 
                         playlist=playlist, 
                         categories=categories,
                         videos=videos,
                         playlist_videos_info=playlist_videos_info)

@app.route('/admin/playlists/delete/<int:playlist_id>')
@login_required
def delete_playlist(playlist_id):
    data = load_data()
    playlists = data.get('playlists', [])
    
    data['playlists'] = [p for p in playlists if p['id'] != playlist_id]
    save_data(data)
    
    return redirect(url_for('admin_playlists'))

@app.route('/admin/videos')
@login_required
def admin_videos():
    data = load_data()
    categories = data.get('categories', [])
    videos = data.get('videos', [])
    playlists = data.get('playlists', [])
    
    # Agregar información adicional a cada video
    for video in videos:
        video['category_name'] = get_category_name(video['category_id'], categories)
        video['playlist_name'] = get_playlist_name(video.get('playlist_id'), playlists)
    
    return render_template('admin_videos.html', 
                         videos=videos, 
                         categories=categories,
                         playlists=playlists)

@app.route('/admin/videos/add', methods=['POST'])
@login_required
def add_video():
    data = load_data()
    videos = data.get('videos', [])
    
    # Procesar videos relacionados
    related_videos_input = request.form.get('related_videos', '')
    related_videos = []
    if related_videos_input:
        try:
            related_videos = [int(x.strip()) for x in related_videos_input.split(',') if x.strip().isdigit()]
        except:
            related_videos = []
    
    # Procesar playlist_id (puede estar vacío)
    playlist_id = request.form.get('playlist_id')
    if playlist_id and playlist_id != 'None':
        playlist_id = int(playlist_id)
    else:
        playlist_id = None
    
    new_video = {
        "id": max([v['id'] for v in videos], default=0) + 1,
        "title": request.form.get('title'),
        "description": request.form.get('description'),
        "video_url": request.form.get('video_url'),
        "thumbnail": request.form.get('thumbnail'),
        "category_id": int(request.form.get('category_id')),
        "playlist_id": playlist_id,
        "views": 0,
        "likes": 0,
        "related_videos": related_videos,
        "created_at": datetime.now().isoformat()
    }
    
    videos.append(new_video)
    data['videos'] = videos
    save_data(data)
    
    return redirect(url_for('admin_videos'))

@app.route('/admin/videos/edit/<int:video_id>', methods=['GET', 'POST'])
@login_required
def edit_video(video_id):
    data = load_data()
    videos = data.get('videos', [])
    categories = data.get('categories', [])
    playlists = data.get('playlists', [])
    
    video = next((v for v in videos if v['id'] == video_id), None)
    if not video:
        return "Video no encontrado", 404
    
    if request.method == 'POST':
        # Procesar videos relacionados
        related_videos_input = request.form.get('related_videos', '')
        related_videos = []
        if related_videos_input:
            try:
                related_videos = [int(x.strip()) for x in related_videos_input.split(',') if x.strip().isdigit()]
            except:
                related_videos = []
        
        # Procesar playlist_id (puede estar vacío)
        playlist_id = request.form.get('playlist_id')
        if playlist_id and playlist_id != 'None':
            playlist_id = int(playlist_id)
        else:
            playlist_id = None
        
        video['title'] = request.form.get('title')
        video['description'] = request.form.get('description')
        video['video_url'] = request.form.get('video_url')
        video['thumbnail'] = request.form.get('thumbnail')
        video['category_id'] = int(request.form.get('category_id'))
        video['playlist_id'] = playlist_id
        video['related_videos'] = related_videos
        
        save_data(data)
        return redirect(url_for('admin_videos'))
    
    # Agregar nombres de videos relacionados para mostrar
    related_videos_info = []
    for related_id in video.get('related_videos', []):
        related_video = next((v for v in videos if v['id'] == related_id), None)
        if related_video:
            related_videos_info.append({
                'id': related_video['id'],
                'title': related_video['title']
            })
    
    return render_template('admin_edit_video.html', 
                         video=video, 
                         categories=categories,
                         playlists=playlists,
                         related_videos_info=related_videos_info,
                         all_videos=[v for v in videos if v['id'] != video_id])

@app.route('/admin/videos/delete/<int:video_id>')
@login_required
def delete_video(video_id):
    data = load_data()
    videos = data.get('videos', [])
    
    data['videos'] = [v for v in videos if v['id'] != video_id]
    save_data(data)
    
    return redirect(url_for('admin_videos'))

@app.route('/admin/export')
@login_required
def export_data():
    data = load_data()
    return jsonify(data)

@app.route('/admin/import', methods=['POST'])
@login_required
def import_data():
    if 'file' not in request.files:
        return "No se seleccionó archivo", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No se seleccionó archivo", 400
    
    if file and file.filename.endswith('.json'):
        try:
            imported_data = json.load(file)
            save_data(imported_data)
            return redirect(url_for('admin_dashboard'))
        except:
            return "Error al importar el archivo", 400
    
    return "Archivo no válido", 400

# API para likes
@app.route('/api/video/<int:video_id>/like', methods=['POST'])
def like_video(video_id):
    data = load_data()
    videos = data.get('videos', [])
    
    video = next((v for v in videos if v['id'] == video_id), None)
    if video:
        video['likes'] = video.get('likes', 0) + 1
        save_data(data)
        return jsonify({'likes': video['likes']})
    
    return jsonify({'error': 'Video no encontrado'}), 404

# API para obtener videos para autocompletado
@app.route('/api/videos/search')
def api_videos_search():
    query = request.args.get('q', '')
    data = load_data()
    videos = data.get('videos', [])
    
    if query:
        results = [{'id': v['id'], 'title': v['title']} 
                  for v in videos if query.lower() in v['title'].lower()][:10]
    else:
        results = []
    
    return jsonify(results)

# API para obtener playlists para autocompletado
@app.route('/api/playlists/search')
def api_playlists_search():
    query = request.args.get('q', '')
    data = load_data()
    playlists = data.get('playlists', [])
    
    if query:
        results = [{'id': p['id'], 'name': p['name']} 
                  for p in playlists if query.lower() in p['name'].lower()][:10]
    else:
        results = []
    
    return jsonify(results)

# Templates HTML embebidos
templates = {
    'index.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VC7Day - La mejor plataforma de videos</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
            --sidebar-width: 240px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
            overflow-x: hidden;
        }
        
        .container {
            display: flex;
            min-height: 100vh;
            position: relative;
        }
        
        /* Sidebar */
        .sidebar {
            width: var(--sidebar-width);
            background: var(--secondary-color);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            padding: 20px 0;
            z-index: 1000;
            transition: transform 0.3s ease;
            left: 0;
            top: 0;
        }
        
        .sidebar-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
        }
        
        .sidebar-overlay.active {
            display: block;
        }
        
        .logo {
            padding: 0 24px 20px;
            border-bottom: 1px solid #373737;
            margin-bottom: 20px;
        }
        
        .logo h1 {
            color: var(--primary-color);
            font-size: 24px;
            font-weight: bold;
        }
        
        .sidebar-section {
            padding: 0 24px;
            margin-bottom: 20px;
        }
        
        .sidebar-item {
            display: flex;
            align-items: center;
            padding: 10px 0;
            color: var(--text-color);
            text-decoration: none;
            transition: background 0.3s;
            border-radius: 10px;
            margin-bottom: 5px;
        }
        
        .sidebar-item:hover {
            background: #373737;
        }
        
        .sidebar-item i {
            margin-right: 15px;
            width: 24px;
            text-align: center;
        }
        
        .category-item {
            display: flex;
            align-items: center;
            padding: 8px 0;
            color: var(--text-color);
            text-decoration: none;
            transition: background 0.3s;
            border-radius: 10px;
        }
        
        .category-item:hover {
            background: #373737;
        }
        
        .category-icon {
            margin-right: 15px;
            width: 24px;
            text-align: center;
            font-size: 18px;
        }
        
        /* Main Content */
        .main-content {
            flex: 1;
            margin-left: var(--sidebar-width);
            padding: 20px;
            transition: margin-left 0.3s ease;
            width: calc(100% - var(--sidebar-width));
        }
        
        /* Header */
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 30px;
            padding: 0 20px;
            position: sticky;
            top: 0;
            background: var(--background-color);
            z-index: 100;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        
        .menu-toggle {
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            padding: 8px;
            border-radius: 50%;
            transition: background 0.3s;
            display: none;
        }
        
        .menu-toggle:hover {
            background: #373737;
        }
        
        .search-bar {
            display: flex;
            flex: 0 1 728px;
            margin: 0 40px;
        }
        
        .search-bar input {
            flex: 1;
            padding: 10px 16px;
            background: #121212;
            border: 1px solid #303030;
            border-radius: 20px 0 0 20px;
            color: var(--text-color);
            font-size: 16px;
        }
        
        .search-bar button {
            padding: 10px 20px;
            background: #303030;
            border: 1px solid #303030;
            border-radius: 0 20px 20px 0;
            color: var(--text-color);
            cursor: pointer;
        }
        
        .admin-btn {
            background: var(--primary-color);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 500;
            white-space: nowrap;
        }
        
        /* Videos Grid */
        .videos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
            padding: 0 20px;
        }
        
        .video-card {
            cursor: pointer;
            transition: transform 0.3s;
            background: var(--secondary-color);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .video-card:hover {
            transform: translateY(-5px);
        }
        
        .video-thumbnail {
            position: relative;
            width: 100%;
            height: 180px;
            overflow: hidden;
            background: #000;
        }
        
        .video-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .video-duration {
            position: absolute;
            bottom: 8px;
            right: 8px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .video-info {
            padding: 12px;
        }
        
        .video-title {
            font-weight: 500;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.3;
            min-height: 2.6em;
        }
        
        .video-meta {
            color: #aaa;
            font-size: 14px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 4px;
        }
        
        .video-views::after {
            content: "•";
            margin: 0 4px;
        }
        
        .playlists-section {
            margin: 40px 20px;
        }
        
        .section-title {
            font-size: 24px;
            margin-bottom: 20px;
            color: var(--text-color);
        }
        
        .playlists-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        
        .playlist-card {
            background: var(--secondary-color);
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            transition: transform 0.3s;
        }
        
        .playlist-card:hover {
            transform: translateY(-5px);
        }
        
        .playlist-thumbnail {
            position: relative;
            width: 100%;
            height: 160px;
            overflow: hidden;
        }
        
        .playlist-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .playlist-video-count {
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .playlist-info {
            padding: 12px;
        }
        
        .playlist-name {
            font-weight: 500;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.3;
        }
        
        .playlist-description {
            color: #aaa;
            font-size: 14px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        /* Responsive */
        @media (max-width: 1200px) {
            .videos-grid {
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            }
        }
        
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
            }
            
            .sidebar.active {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
                width: 100%;
            }
            
            .menu-toggle {
                display: block;
            }
            
            .header {
                padding: 10px 15px;
            }
            
            .search-bar {
                margin: 0 15px;
                flex: 1;
            }
            
            .admin-btn {
                padding: 8px 12px;
                font-size: 14px;
            }
            
            .videos-grid {
                grid-template-columns: 1fr;
                padding: 0 10px;
                gap: 15px;
            }
            
            .video-thumbnail {
                height: 200px;
            }
            
            .playlists-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 480px) {
            .search-bar {
                margin: 0 10px;
            }
            
            .search-bar input {
                padding: 8px 12px;
                font-size: 14px;
            }
            
            .search-bar button {
                padding: 8px 15px;
            }
            
            .admin-btn {
                padding: 6px 10px;
                font-size: 12px;
            }
            
            .video-thumbnail {
                height: 180px;
            }
            
            .videos-grid {
                gap: 12px;
            }
        }
        /* 3 LÍNEAS MÁXIMO PARA TEXTOS */

/* Títulos de videos - 3 líneas */
.video-title,
.search-title,
.related-title,
.playlist-name {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.3;
    max-height: 3.9em; /* 3 líneas * 1.3 line-height */
}

/* Descripciones - 3 líneas */
.video-description,
.playlist-description,
.description-text,
.search-description {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.4;
    max-height: 4.2em; /* 3 líneas * 1.4 line-height */
}

/* Asegurar que el texto se rompa correctamente */
.video-title,
.search-title,
.related-title,
.playlist-name,
.video-description,
.playlist-description,
.description-text,
.search-description {
    word-wrap: break-word;
    word-break: break-word;
    overflow-wrap: break-word;
}
    </style>
</head>
<body>
    <!-- Overlay para móviles -->
    <div class="sidebar-overlay" id="sidebarOverlay"></div>
    
    <div class="container">
        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="logo">
                <h1>VC7Day</h1>
            </div>
            
            <div class="sidebar-section">
                <a href="/" class="sidebar-item">
                    <i class="fas fa-home"></i> Inicio
                </a>
                <a href="#" class="sidebar-item">
                    <i class="fas fa-fire"></i> Tendencias
                </a>
                <a href="#" class="sidebar-item">
                    <i class="fas fa-history"></i> Historial
                </a>
            </div>
            
            <div class="sidebar-section">
                <h3 style="color: #aaa; font-size: 14px; margin-bottom: 15px; padding: 0 24px;">CATEGORÍAS</h3>
                {% for category in categories %}
                <a href="/category/{{ category.id }}" class="category-item">
                    <span class="category-icon">{{ category.icon }}</span>
                    {{ category.name }}
                </a>
                {% endfor %}
            </div>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <!-- Header -->
            <header class="header">
                <button class="menu-toggle" id="menuToggle">
                    <i class="fas fa-bars"></i>
                </button>
                
                <form class="search-bar" action="/search" method="GET">
                    <input type="text" name="q" placeholder="Buscar videos..." value="">
                    <button type="submit"><i class="fas fa-search"></i></button>
                </form>
                
                <a href="/admin/login" class="admin-btn">
                    <i class="fas fa-cog"></i> Admin
                </a>
            </header>

            <!-- Playlists Section -->
            {% if playlists %}
            <section class="playlists-section">
                <h2 class="section-title">Playlists Destacadas</h2>
                <div class="playlists-grid">
                    {% for playlist in playlists %}
                    <div class="playlist-card" onclick="window.location.href='/playlist/{{ playlist.id }}'">
                        <div class="playlist-thumbnail">
                            <img src="{{ playlist.thumbnail }}" alt="{{ playlist.name }}" 
                                 onerror="this.src='https://via.placeholder.com/320x180/333333/ffffff?text=Playlist'">
                            <div class="playlist-video-count">{{ playlist.videos|length }} videos</div>
                        </div>
                        <div class="playlist-info">
                            <h3 class="playlist-name">{{ playlist.name }}</h3>
                            <p class="playlist-description">{{ playlist.description }}</p>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endif %}

            <!-- Videos Grid -->
            <section class="videos-grid">
                {% for video in videos %}
                <div class="video-card" onclick="window.location.href='/video/{{ video.id }}'">
                    <div class="video-thumbnail">
                        <img src="{{ video.thumbnail }}" alt="{{ video.title }}" 
                             onerror="this.src='https://via.placeholder.com/320x180/333333/ffffff?text=Thumbnail'">
                        <div class="video-duration">10:30</div>
                    </div>
                    <div class="video-info">
                        <h3 class="video-title">{{ video.title }}</h3>
                        <div class="video-meta">
                            <span class="video-views">{{ video.views }} vistas</span>
                            <span>hace 2 días</span>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </section>
        </main>
    </div>

    <script>
        // Elementos del DOM
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');
        const sidebarOverlay = document.getElementById('sidebarOverlay');
        const mainContent = document.querySelector('.main-content');
        
        // Función para alternar el sidebar
        function toggleSidebar() {
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
            document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
        }
        
        // Event listeners
        menuToggle.addEventListener('click', toggleSidebar);
        sidebarOverlay.addEventListener('click', toggleSidebar);
        
        // Cerrar sidebar al hacer clic en un enlace (en móviles)
        sidebar.addEventListener('click', (e) => {
            if (e.target.tagName === 'A' && window.innerWidth <= 768) {
                toggleSidebar();
            }
        });
        
        // Cerrar sidebar al redimensionar la ventana si se vuelve a escritorio
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    </script>
</body>
</html>
''',

    'category.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ current_category.name }} - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
            --sidebar-width: 240px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
            overflow-x: hidden;
        }
        
        .container {
            display: flex;
            min-height: 100vh;
            position: relative;
        }
        
        .sidebar {
            width: var(--sidebar-width);
            background: var(--secondary-color);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            padding: 20px 0;
            z-index: 1000;
            transition: transform 0.3s ease;
            left: 0;
            top: 0;
        }
        
        .sidebar-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
        }
        
        .sidebar-overlay.active {
            display: block;
        }
        
        .logo {
            padding: 0 24px 20px;
            border-bottom: 1px solid #373737;
            margin-bottom: 20px;
        }
        
        .logo h1 {
            color: var(--primary-color);
            font-size: 24px;
            font-weight: bold;
        }
        
        .sidebar-section {
            padding: 0 24px;
            margin-bottom: 20px;
        }
        
        .sidebar-item {
            display: flex;
            align-items: center;
            padding: 10px 0;
            color: var(--text-color);
            text-decoration: none;
            transition: background 0.3s;
            border-radius: 10px;
            margin-bottom: 5px;
        }
        
        .sidebar-item:hover {
            background: #373737;
        }
        
        .sidebar-item i {
            margin-right: 15px;
            width: 24px;
            text-align: center;
        }
        
        .category-item {
            display: flex;
            align-items: center;
            padding: 8px 0;
            color: var(--text-color);
            text-decoration: none;
            transition: background 0.3s;
            border-radius: 10px;
        }
        
        .category-item:hover {
            background: #373737;
        }
        
        .category-icon {
            margin-right: 15px;
            width: 24px;
            text-align: center;
            font-size: 18px;
        }
        
        .main-content {
            flex: 1;
            margin-left: var(--sidebar-width);
            padding: 20px;
            transition: margin-left 0.3s ease;
            width: calc(100% - var(--sidebar-width));
        }
        
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 30px;
            padding: 0 20px;
            position: sticky;
            top: 0;
            background: var(--background-color);
            z-index: 100;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        
        .menu-toggle {
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            padding: 8px;
            border-radius: 50%;
            transition: background 0.3s;
            display: none;
        }
        
        .menu-toggle:hover {
            background: #373737;
        }
        
        .search-bar {
            display: flex;
            flex: 0 1 728px;
            margin: 0 40px;
        }
        
        .search-bar input {
            flex: 1;
            padding: 10px 16px;
            background: #121212;
            border: 1px solid #303030;
            border-radius: 20px 0 0 20px;
            color: var(--text-color);
            font-size: 16px;
        }
        
        .search-bar button {
            padding: 10px 20px;
            background: #303030;
            border: 1px solid #303030;
            border-radius: 0 20px 20px 0;
            color: var(--text-color);
            cursor: pointer;
        }
        
        .admin-btn {
            background: var(--primary-color);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 500;
            white-space: nowrap;
        }
        
        .category-header {
            padding: 0 20px 30px;
            text-align: center;
        }
        
        .category-icon-large {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        .category-title {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .category-description {
            color: #aaa;
            font-size: 16px;
        }
        
        .videos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
            padding: 0 20px;
            margin-bottom: 40px;
        }
        
        .video-card {
            cursor: pointer;
            transition: transform 0.3s;
            background: var(--secondary-color);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .video-card:hover {
            transform: translateY(-5px);
        }
        
        .video-thumbnail {
            position: relative;
            width: 100%;
            height: 180px;
            overflow: hidden;
            background: #000;
        }
        
        .video-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .video-duration {
            position: absolute;
            bottom: 8px;
            right: 8px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .video-info {
            padding: 12px;
        }
        
        .video-title {
            font-weight: 500;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.3;
            min-height: 2.6em;
        }
        
        .video-meta {
            color: #aaa;
            font-size: 14px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 4px;
        }
        
        .video-views::after {
            content: "•";
            margin: 0 4px;
        }
        
        .playlists-section {
            margin: 40px 20px;
        }
        
        .section-title {
            font-size: 24px;
            margin-bottom: 20px;
            color: var(--text-color);
        }
        
        .playlists-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        
        .playlist-card {
            background: var(--secondary-color);
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            transition: transform 0.3s;
        }
        
        .playlist-card:hover {
            transform: translateY(-5px);
        }
        
        .playlist-thumbnail {
            position: relative;
            width: 100%;
            height: 160px;
            overflow: hidden;
        }
        
        .playlist-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .playlist-video-count {
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .playlist-info {
            padding: 12px;
        }
        
        .playlist-name {
            font-weight: 500;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.3;
        }
        
        .playlist-description {
            color: #aaa;
            font-size: 14px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
            }
            
            .sidebar.active {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
                width: 100%;
            }
            
            .menu-toggle {
                display: block;
            }
            
            .header {
                padding: 10px 15px;
            }
            
            .search-bar {
                margin: 0 15px;
                flex: 1;
            }
            
            .videos-grid {
                grid-template-columns: 1fr;
                padding: 0 10px;
            }
            
            .category-header {
                padding: 0 15px 20px;
            }
            
            .category-title {
                font-size: 24px;
            }
            
            .playlists-grid {
                grid-template-columns: 1fr;
            }
        }
        /* 3 LÍNEAS MÁXIMO PARA TEXTOS */

/* Títulos de videos - 3 líneas */
.video-title,
.search-title,
.related-title,
.playlist-name {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.3;
    max-height: 3.9em; /* 3 líneas * 1.3 line-height */
}

/* Descripciones - 3 líneas */
.video-description,
.playlist-description,
.description-text,
.search-description {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.4;
    max-height: 4.2em; /* 3 líneas * 1.4 line-height */
}

/* Asegurar que el texto se rompa correctamente */
.video-title,
.search-title,
.related-title,
.playlist-name,
.video-description,
.playlist-description,
.description-text,
.search-description {
    word-wrap: break-word;
    word-break: break-word;
    overflow-wrap: break-word;
}
    </style>
</head>
<body>
    <!-- Overlay para móviles -->
    <div class="sidebar-overlay" id="sidebarOverlay"></div>
    
    <div class="container">
        <aside class="sidebar" id="sidebar">
            <div class="logo">
                <h1>VC7Day</h1>
            </div>
            
            <div class="sidebar-section">
                <a href="/" class="sidebar-item">
                    <i class="fas fa-home"></i> Inicio
                </a>
                <a href="#" class="sidebar-item">
                    <i class="fas fa-fire"></i> Tendencias
                </a>
            </div>
            
            <div class="sidebar-section">
                <h3 style="color: #aaa; font-size: 14px; margin-bottom: 15px; padding: 0 24px;">CATEGORÍAS</h3>
                {% for category in categories %}
                <a href="/category/{{ category.id }}" class="category-item {% if current_category.id == category.id %}active{% endif %}">
                    <span class="category-icon">{{ category.icon }}</span>
                    {{ category.name }}
                </a>
                {% endfor %}
            </div>
        </aside>

        <main class="main-content">
            <header class="header">
                <button class="menu-toggle" id="menuToggle">
                    <i class="fas fa-bars"></i>
                </button>
                
                <form class="search-bar" action="/search" method="GET">
                    <input type="text" name="q" placeholder="Buscar videos...">
                    <button type="submit"><i class="fas fa-search"></i></button>
                </form>
                
                <a href="/admin/login" class="admin-btn">
                    <i class="fas fa-cog"></i> Admin
                </a>
            </header>

            <div class="category-header">
                <div class="category-icon-large">{{ current_category.icon }}</div>
                <h1 class="category-title">{{ current_category.name }}</h1>
                <p class="category-description">{{ videos|length }} videos • {{ playlists|length }} playlists en esta categoría</p>
            </div>

            {% if playlists %}
            <section class="playlists-section">
                <h2 class="section-title">Playlists de {{ current_category.name }}</h2>
                <div class="playlists-grid">
                    {% for playlist in playlists %}
                    <div class="playlist-card" onclick="window.location.href='/playlist/{{ playlist.id }}'">
                        <div class="playlist-thumbnail">
                            <img src="{{ playlist.thumbnail }}" alt="{{ playlist.name }}" 
                                 onerror="this.src='https://via.placeholder.com/320x180/333333/ffffff?text=Playlist'">
                            <div class="playlist-video-count">{{ playlist.videos|length }} videos</div>
                        </div>
                        <div class="playlist-info">
                            <h3 class="playlist-name">{{ playlist.name }}</h3>
                            <p class="playlist-description">{{ playlist.description }}</p>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endif %}

            <div class="videos-grid">
                {% for video in videos %}
                <div class="video-card" onclick="window.location.href='/video/{{ video.id }}'">
                    <div class="video-thumbnail">
                        <img src="{{ video.thumbnail }}" alt="{{ video.title }}"
                             onerror="this.src='https://via.placeholder.com/320x180/333333/ffffff?text=Thumbnail'">
                        <div class="video-duration">10:30</div>
                    </div>
                    <div class="video-info">
                        <h3 class="video-title">{{ video.title }}</h3>
                        <div class="video-meta">
                            <span class="video-views">{{ video.views }} vistas</span>
                            <span>hace 2 días</span>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </main>
    </div>

    <script>
        // Elementos del DOM
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');
        const sidebarOverlay = document.getElementById('sidebarOverlay');
        
        // Función para alternar el sidebar
        function toggleSidebar() {
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
            document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
        }
        
        // Event listeners
        menuToggle.addEventListener('click', toggleSidebar);
        sidebarOverlay.addEventListener('click', toggleSidebar);
        
        // Cerrar sidebar al hacer clic en un enlace (en móviles)
        sidebar.addEventListener('click', (e) => {
            if (e.target.tagName === 'A' && window.innerWidth <= 768) {
                toggleSidebar();
            }
        });
        
        // Cerrar sidebar al redimensionar la ventana si se vuelve a escritorio
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    </script>
</body>
</html>
''',

    'playlist.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ playlist.name }} - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }
        
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px;
            border-bottom: 1px solid #373737;
        }
        
        .logo {
            color: var(--primary-color);
            font-size: 24px;
            font-weight: bold;
            text-decoration: none;
        }
        
        .search-bar {
            display: flex;
            flex: 0 1 728px;
            margin: 0 40px;
        }
        
        .search-bar input {
            flex: 1;
            padding: 10px 16px;
            background: #121212;
            border: 1px solid #303030;
            border-radius: 20px 0 0 20px;
            color: var(--text-color);
            font-size: 16px;
        }
        
        .search-bar button {
            padding: 10px 20px;
            background: #303030;
            border: 1px solid #303030;
            border-radius: 0 20px 20px 0;
            color: var(--text-color);
            cursor: pointer;
        }
        
        .admin-btn {
            background: var(--primary-color);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 500;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .playlist-header {
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
            align-items: flex-start;
        }
        
        .playlist-thumbnail-large {
            width: 320px;
            height: 180px;
            border-radius: 12px;
            overflow: hidden;
            flex-shrink: 0;
        }
        
        .playlist-thumbnail-large img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .playlist-info {
            flex: 1;
        }
        
        .playlist-title {
            font-size: 28px;
            margin-bottom: 10px;
            line-height: 1.3;
        }
        
        .playlist-meta {
            color: #aaa;
            margin-bottom: 15px;
            font-size: 14px;
        }
        
        .playlist-description {
            color: #ddd;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        
        .playlist-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: var(--primary-color);
            color: white;
        }
        
        .btn-secondary {
            background: #373737;
            color: white;
        }
        
        .videos-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .playlist-video {
            display: flex;
            cursor: pointer;
            transition: background 0.3s;
            padding: 16px;
            border-radius: 12px;
            background: var(--secondary-color);
        }
        
        .playlist-video:hover {
            background: #373737;
        }
        
        .video-number {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            font-size: 18px;
            font-weight: bold;
            color: #aaa;
            margin-right: 16px;
            flex-shrink: 0;
        }
        
        .video-thumbnail-small {
            width: 200px;
            height: 112px;
            border-radius: 8px;
            overflow: hidden;
            margin-right: 16px;
            flex-shrink: 0;
        }
        
        .video-thumbnail-small img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .video-info {
            flex: 1;
        }
        
        .video-title {
            font-weight: 500;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.3;
        }
        
        .video-meta {
            color: #aaa;
            font-size: 14px;
        }
        
        .video-duration {
            color: #aaa;
            font-size: 14px;
            margin-left: auto;
            padding-left: 16px;
            display: flex;
            align-items: center;
            flex-shrink: 0;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #aaa;
        }
        
        .empty-state i {
            font-size: 48px;
            margin-bottom: 20px;
            color: #555;
        }
        
        @media (max-width: 768px) {
            .playlist-header {
                flex-direction: column;
                text-align: center;
            }
            
            .playlist-thumbnail-large {
                width: 100%;
                height: 200px;
                margin: 0 auto;
            }
            
            .playlist-actions {
                justify-content: center;
            }
            
            .playlist-video {
                flex-direction: column;
            }
            
            .video-number {
                display: none;
            }
            
            .video-thumbnail-small {
                width: 100%;
                height: 180px;
                margin-right: 0;
                margin-bottom: 12px;
            }
            
            .video-duration {
                margin-left: 0;
                padding-left: 0;
                margin-top: 8px;
            }
            
            .search-bar {
                margin: 0 20px;
            }
            
            .header {
                padding: 15px;
            }
        }
        
        @media (max-width: 480px) {
            .search-bar {
                margin: 0 10px;
            }
            
            .search-bar input {
                padding: 8px 12px;
                font-size: 14px;
            }
            
            .search-bar button {
                padding: 8px 15px;
            }
            
            .admin-btn {
                padding: 6px 12px;
                font-size: 14px;
            }
            
            .playlist-title {
                font-size: 24px;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">VC7Day</a>
        
        <form class="search-bar" action="/search" method="GET">
            <input type="text" name="q" placeholder="Buscar videos...">
            <button type="submit"><i class="fas fa-search"></i></button>
        </form>
        
        <a href="/admin/login" class="admin-btn">
            <i class="fas fa-cog"></i> Admin
        </a>
    </header>

    <div class="container">
        <div class="playlist-header">
            <div class="playlist-thumbnail-large">
                <img src="{{ playlist.thumbnail }}" alt="{{ playlist.name }}"
                     onerror="this.src='https://via.placeholder.com/320x180/333333/ffffff?text=Playlist'">
            </div>
            <div class="playlist-info">
                <h1 class="playlist-title">{{ playlist.name }}</h1>
                <div class="playlist-meta">
                    {{ videos|length }} videos • 
                    {% if category %}
                    Categoría: {{ category.name }}
                    {% endif %}
                </div>
                <p class="playlist-description">{{ playlist.description }}</p>
                <div class="playlist-actions">
                    <button class="btn btn-primary">
                        <i class="fas fa-play"></i> Reproducir todo
                    </button>
                    <button class="btn btn-secondary">
                        <i class="fas fa-shuffle"></i> Mezclar
                    </button>
                </div>
            </div>
        </div>

        <div class="videos-list">
            {% if videos %}
                {% for video in videos %}
                <div class="playlist-video" onclick="window.location.href='/video/{{ video.id }}'">
                    <div class="video-number">{{ loop.index }}</div>
                    <div class="video-thumbnail-small">
                        <img src="{{ video.thumbnail }}" alt="{{ video.title }}"
                             onerror="this.src='https://via.placeholder.com/200x112/333333/ffffff?text=Thumbnail'">
                    </div>
                    <div class="video-info">
                        <h3 class="video-title">{{ video.title }}</h3>
                        <div class="video-meta">
                            {{ video.views }} vistas • {{ video.likes }} likes
                        </div>
                    </div>
                    <div class="video-duration">10:30</div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <i class="fas fa-film"></i>
                    <h3>No hay videos en esta playlist</h3>
                    <p>Esta playlist está vacía por el momento.</p>
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
''',

    'watch.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ video.title }} - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }
        
        .container {
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            gap: 24px;
        }
        
        .video-container {
            flex: 1;
        }
        
        .video-player {
            width: 100%;
            background: #000;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .video-player video {
            width: 100%;
            height: auto;
            max-height: 70vh;
        }
        
        .video-info {
            margin-bottom: 20px;
        }
        
        .video-title {
            font-size: 20px;
            font-weight: 500;
            margin-bottom: 12px;
            line-height: 1.4;
        }
        
        .video-stats {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 16px;
            border-bottom: 1px solid #373737;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .video-views {
            color: #aaa;
            font-size: 14px;
        }
        
        .video-actions {
            display: flex;
            gap: 16px;
        }
        
        .action-btn {
            background: none;
            border: none;
            color: #aaa;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 14px;
            transition: color 0.3s;
            padding: 8px 12px;
            border-radius: 20px;
        }
        
        .action-btn:hover {
            background: #272727;
            color: var(--text-color);
        }
        
        .action-btn.like:hover {
            color: var(--primary-color);
        }
        
        .channel-info {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
            gap: 12px;
        }
        
        .channel-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: var(--primary-color);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
            flex-shrink: 0;
        }
        
        .channel-details {
            flex: 1;
        }
        
        .channel-name {
            font-weight: 500;
            margin-bottom: 4px;
        }
        
        .channel-subs {
            color: #aaa;
            font-size: 14px;
        }
        
        .subscribe-btn {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 500;
            flex-shrink: 0;
        }
        
        .video-description {
            background: #272727;
            padding: 16px;
            border-radius: 12px;
            margin-top: 16px;
        }
        
        .description-text {
            color: #aaa;
            font-size: 14px;
            line-height: 1.8;
            white-space: pre-line;
        }
        
        .playlist-info {
            background: #272727;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .playlist-info:hover {
            background: #373737;
        }
        
        .playlist-title {
            font-weight: 500;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .playlist-meta {
            color: #aaa;
            font-size: 14px;
        }
        
        .sidebar {
            width: 400px;
            flex-shrink: 0;
        }
        
        .related-videos {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .related-video {
            display: flex;
            cursor: pointer;
            transition: background 0.3s;
            padding: 8px;
            border-radius: 8px;
        }
        
        .related-video:hover {
            background: #272727;
        }
        
        .related-thumbnail {
            width: 168px;
            height: 94px;
            border-radius: 8px;
            overflow: hidden;
            margin-right: 12px;
            flex-shrink: 0;
        }
        
        .related-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .related-info {
            flex: 1;
        }
        
        .related-title {
            font-weight: 500;
            font-size: 14px;
            margin-bottom: 4px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.3;
        }
        
        .related-channel {
            color: #aaa;
            font-size: 12px;
            margin-bottom: 2px;
        }
        
        .related-meta {
            color: #aaa;
            font-size: 12px;
        }
        
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px 20px;
            border-bottom: 1px solid #373737;
            margin-bottom: 20px;
        }
        
        .logo {
            color: var(--primary-color);
            font-size: 24px;
            font-weight: bold;
            text-decoration: none;
        }
        
        .search-bar {
            display: flex;
            flex: 0 1 728px;
            margin: 0 40px;
        }
        
        .search-bar input {
            flex: 1;
            padding: 10px 16px;
            background: #121212;
            border: 1px solid #303030;
            border-radius: 20px 0 0 20px;
            color: var(--text-color);
            font-size: 16px;
        }
        
        .search-bar button {
            padding: 10px 20px;
            background: #303030;
            border: 1px solid #303030;
            border-radius: 0 20px 20px 0;
            color: var(--text-color);
            cursor: pointer;
        }
        
        @media (max-width: 1200px) {
            .container {
                flex-direction: column;
            }
            
            .video-container {
                margin-right: 0;
                margin-bottom: 24px;
            }
            
            .sidebar {
                width: 100%;
            }
        }
        
        @media (max-width: 768px) {
            .video-player video {
                max-height: 50vh;
            }
            
            .video-stats {
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }
            
            .video-actions {
                width: 100%;
                justify-content: space-between;
            }
            
            .channel-info {
                flex-direction: column;
                text-align: center;
                gap: 16px;
            }
            
            .search-bar {
                margin: 0 20px;
            }
            
            .container {
                padding: 15px;
            }
            
            .header {
                padding: 0 15px 15px;
            }
            
            .related-video {
                flex-direction: column;
            }
            
            .related-thumbnail {
                width: 100%;
                height: 180px;
                margin-right: 0;
                margin-bottom: 8px;
            }
        }
        
        @media (max-width: 480px) {
            .video-player video {
                max-height: 40vh;
            }
            
            .search-bar {
                margin: 0 10px;
            }
            
            .search-bar input {
                padding: 8px 12px;
                font-size: 14px;
            }
            
            .search-bar button {
                padding: 8px 15px;
            }
            
            .video-title {
                font-size: 18px;
            }
        }
        /* 3 LÍNEAS MÁXIMO PARA TEXTOS */

/* Títulos de videos - 3 líneas */
.video-title,
.search-title,
.related-title,
.playlist-name {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.3;
    max-height: 3.9em; /* 3 líneas * 1.3 line-height */
}

/* Descripciones - 3 líneas */
.video-description,
.playlist-description,
.description-text,
.search-description {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.4;
    max-height: 4.2em; /* 3 líneas * 1.4 line-height */
}

/* Asegurar que el texto se rompa correctamente */
.video-title,
.search-title,
.related-title,
.playlist-name,
.video-description,
.playlist-description,
.description-text,
.search-description {
    word-wrap: break-word;
    word-break: break-word;
    overflow-wrap: break-word;
}
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">VC7Day</a>
        
        <form class="search-bar" action="/search" method="GET">
            <input type="text" name="q" placeholder="Buscar videos...">
            <button type="submit"><i class="fas fa-search"></i></button>
        </form>
        
        <a href="/admin/login" style="color: #aaa; text-decoration: none;">
            <i class="fas fa-cog"></i>
        </a>
    </header>

    <div class="container">
        <div class="video-container">
            {% if video_playlist %}
            <div class="playlist-info" onclick="window.location.href='/playlist/{{ video_playlist.id }}'">
                <div class="playlist-title">
                    <i class="fas fa-list"></i>
                    {{ video_playlist.name }}
                </div>
                <div class="playlist-meta">Reproduciendo desde playlist</div>
            </div>
            {% endif %}
            
            <div class="video-player">
                <video 
                    controls 
                    poster="{{ video.thumbnail }}"
                    preload="metadata"
                >
                    <source src="{{ video.video_url }}" type="video/mp4">
                    Tu navegador no soporta el elemento de video.
                </video>
            </div>
            
            <div class="video-info">
                <h1 class="video-title">{{ video.title }}</h1>
                
                <div class="video-stats">
                    <div class="video-views">
                        {{ video.views }} vistas • 
                        {% if video_category %}
                        {{ video_category.name }}
                        {% else %}
                        Sin categoría
                        {% endif %}
                    </div>
                    <div class="video-actions">
                        <button class="action-btn like" onclick="likeVideo({{ video.id }})">
                            <i class="fas fa-thumbs-up"></i>
                            <span id="likes-count">{{ video.likes }}</span>
                        </button>
                        <button class="action-btn">
                            <i class="fas fa-share"></i> Compartir
                        </button>
                        <button class="action-btn">
                            <i class="fas fa-download"></i> Descargar
                        </button>
                    </div>
                </div>
                
                <div class="channel-info">
                    <div class="channel-avatar">VC</div>
                    <div class="channel-details">
                        <div class="channel-name">VC7Day Channel</div>
                        <div class="channel-subs">1.2M suscriptores</div>
                    </div>
                    <button class="subscribe-btn">Suscribirse</button>
                </div>
                
                <div class="video-description">
                    <div class="description-text">
                        {{ video.description }}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="sidebar">
            <h3 style="margin-bottom: 16px;">Videos relacionados</h3>
            <div class="related-videos">
                {% for related in related_videos %}
                <div class="related-video" onclick="window.location.href='/video/{{ related.id }}'">
                    <div class="related-thumbnail">
                        <img src="{{ related.thumbnail }}" alt="{{ related.title }}"
                             onerror="this.src='https://via.placeholder.com/168x94/333333/ffffff?text=Thumbnail'">
                    </div>
                    <div class="related-info">
                        <div class="related-title">{{ related.title }}</div>
                        <div class="related-channel">VC7Day Channel</div>
                        <div class="related-meta">{{ related.views }} vistas • hace 2 días</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        async function likeVideo(videoId) {
            try {
                const response = await fetch(`/api/video/${videoId}/like`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                const data = await response.json();
                if (data.likes) {
                    document.getElementById('likes-count').textContent = data.likes;
                    
                    // Efecto visual
                    const likeBtn = document.querySelector('.action-btn.like');
                    likeBtn.style.color = 'var(--primary-color)';
                    setTimeout(() => {
                        likeBtn.style.color = '';
                    }, 1000);
                }
            } catch (error) {
                console.error('Error al dar like:', error);
            }
        }
        
        // Mejorar la experiencia del reproductor
        const video = document.querySelector('video');
        video.addEventListener('loadeddata', function() {
            console.log('Video cargado correctamente');
        });
        
        video.addEventListener('error', function() {
            console.error('Error al cargar el video');
            alert('Error al cargar el video. Por favor, verifica la URL.');
        });
        
        // Navegación con teclado
        document.addEventListener('keydown', function(e) {
            if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                if (e.key === 'ArrowLeft') {
                    video.currentTime -= 10;
                } else if (e.key === 'ArrowRight') {
                    video.currentTime += 10;
                } else if (e.key === ' ') {
                    e.preventDefault();
                    if (video.paused) {
                        video.play();
                    } else {
                        video.pause();
                    }
                }
            }
        });
    </script>
</body>
</html>
''',

    'search.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Buscar: {{ search_query }} - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }
        
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px;
            border-bottom: 1px solid #373737;
        }
        
        .logo {
            color: var(--primary-color);
            font-size: 24px;
            font-weight: bold;
            text-decoration: none;
        }
        
        .search-bar {
            display: flex;
            flex: 0 1 728px;
            margin: 0 40px;
        }
        
        .search-bar input {
            flex: 1;
            padding: 10px 16px;
            background: #121212;
            border: 1px solid #303030;
            border-radius: 20px 0 0 20px;
            color: var(--text-color);
            font-size: 16px;
        }
        
        .search-bar button {
            padding: 10px 20px;
            background: #303030;
            border: 1px solid #303030;
            border-radius: 0 20px 20px 0;
            color: var(--text-color);
            cursor: pointer;
        }
        
        .admin-btn {
            background: var(--primary-color);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 500;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .search-results {
            margin-bottom: 30px;
        }
        
        .search-query {
            font-size: 18px;
            margin-bottom: 20px;
            color: #aaa;
        }
        
        .results-count {
            color: #aaa;
            margin-bottom: 20px;
        }
        
        .results-tabs {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            border-bottom: 1px solid #373737;
        }
        
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: border-color 0.3s;
        }
        
        .tab.active {
            border-bottom-color: var(--primary-color);
            color: var(--primary-color);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .video-results, .playlist-results {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .search-video, .search-playlist {
            display: flex;
            cursor: pointer;
            transition: background 0.3s;
            padding: 16px;
            border-radius: 12px;
            background: var(--secondary-color);
        }
        
        .search-video:hover, .search-playlist:hover {
            background: #373737;
        }
        
        .search-thumbnail {
            width: 360px;
            height: 202px;
            border-radius: 12px;
            overflow: hidden;
            margin-right: 16px;
            flex-shrink: 0;
        }
        
        .search-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .search-info {
            flex: 1;
        }
        
        .search-title {
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.3;
        }
        
        .search-meta {
            color: #aaa;
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .search-channel {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .channel-avatar-small {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: var(--primary-color);
            margin-right: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
        }
        
        .search-description {
            color: #aaa;
            font-size: 14px;
            line-height: 1.6;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .playlist-thumbnail {
            width: 200px;
            height: 112px;
            border-radius: 8px;
            overflow: hidden;
            margin-right: 16px;
            flex-shrink: 0;
            position: relative;
        }
        
        .playlist-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .playlist-video-count {
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #aaa;
        }
        
        .empty-state i {
            font-size: 48px;
            margin-bottom: 20px;
            color: #555;
        }
        
        @media (max-width: 768px) {
            .search-video, .search-playlist {
                flex-direction: column;
            }
            
            .search-thumbnail, .playlist-thumbnail {
                width: 100%;
                height: 200px;
                margin-right: 0;
                margin-bottom: 12px;
            }
            
            .search-bar {
                margin: 0 20px;
            }
            
            .header {
                padding: 15px;
            }
            
            .container {
                padding: 15px;
            }
            
            .results-tabs {
                flex-direction: column;
                gap: 10px;
            }
        }
        
        @media (max-width: 480px) {
            .search-bar {
                margin: 0 10px;
            }
            
            .search-bar input {
                padding: 8px 12px;
                font-size: 14px;
            }
            
            .search-bar button {
                padding: 8px 15px;
            }
            
            .admin-btn {
                padding: 6px 12px;
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">VC7Day</a>
        
        <form class="search-bar" action="/search" method="GET">
            <input type="text" name="q" placeholder="Buscar videos..." value="{{ search_query }}">
            <button type="submit"><i class="fas fa-search"></i></button>
        </form>
        
        <a href="/admin/login" class="admin-btn">
            <i class="fas fa-cog"></i> Admin
        </a>
    </header>

    <div class="container">
        <div class="search-results">
            <div class="search-query">
                Resultados de búsqueda para: "{{ search_query }}"
            </div>
            
            <div class="results-count">
                {{ videos|length + playlists|length }} resultados encontrados
            </div>
            
            <div class="results-tabs">
                <div class="tab active" data-tab="videos">Videos ({{ videos|length }})</div>
                <div class="tab" data-tab="playlists">Playlists ({{ playlists|length }})</div>
            </div>
            
            <div class="tab-content active" id="videos-tab">
                <div class="video-results">
                    {% for video in videos %}
                    <div class="search-video" onclick="window.location.href='/video/{{ video.id }}'">
                        <div class="search-thumbnail">
                            <img src="{{ video.thumbnail }}" alt="{{ video.title }}"
                                 onerror="this.src='https://via.placeholder.com/360x202/333333/ffffff?text=Thumbnail'">
                        </div>
                        <div class="search-info">
                            <h3 class="search-title">{{ video.title }}</h3>
                            <div class="search-meta">
                                {{ video.views }} vistas • hace 2 días
                            </div>
                            <div class="search-channel">
                                <div class="channel-avatar-small">VC</div>
                                <span>VC7Day Channel</span>
                            </div>
                            <div class="search-description">
                                {{ video.description }}
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                    
                    {% if not videos %}
                    <div class="empty-state">
                        <i class="fas fa-film"></i>
                        <h3>No se encontraron videos</h3>
                        <p>Intenta con otros términos de búsqueda</p>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <div class="tab-content" id="playlists-tab">
                <div class="playlist-results">
                    {% for playlist in playlists %}
                    <div class="search-playlist" onclick="window.location.href='/playlist/{{ playlist.id }}'">
                        <div class="playlist-thumbnail">
                            <img src="{{ playlist.thumbnail }}" alt="{{ playlist.name }}"
                                 onerror="this.src='https://via.placeholder.com/200x112/333333/ffffff?text=Playlist'">
                            <div class="playlist-video-count">{{ playlist.videos|length }} videos</div>
                        </div>
                        <div class="search-info">
                            <h3 class="search-title">{{ playlist.name }}</h3>
                            <div class="search-meta">
                                Playlist • {{ playlist.videos|length }} videos
                            </div>
                            <div class="search-description">
                                {{ playlist.description }}
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                    
                    {% if not playlists %}
                    <div class="empty-state">
                        <i class="fas fa-list"></i>
                        <h3>No se encontraron playlists</h3>
                        <p>Intenta con otros términos de búsqueda</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <script>
        // Tabs functionality
        const tabs = document.querySelectorAll('.tab');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs and contents
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                tab.classList.add('active');
                const tabId = tab.getAttribute('data-tab') + '-tab';
                document.getElementById(tabId).classList.add('active');
            });
        });
    </script>
</body>
</html>
''',

    'admin_login.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - VC7Day</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 3rem;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            width: 100%;
            max-width: 400px;
            color: white;
        }
        
        .login-title {
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
        }
        
        input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 1rem;
        }
        
        input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .btn {
            width: 100%;
            padding: 0.75rem;
            background: #ff0000;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #cc0000;
        }
        
        .error {
            color: #ff6b6b;
            text-align: center;
            margin-top: 1rem;
        }
        
        .back-link {
            text-align: center;
            margin-top: 1rem;
        }
        
        .back-link a {
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
        }
        
        .back-link a:hover {
            color: white;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1 class="login-title">VC7Day Admin</h1>
        <form method="POST">
            <div class="form-group">
                <label for="password">Contraseña:</label>
                <input type="password" id="password" name="password" required placeholder="Ingresa la contraseña">
            </div>
            <button type="submit" class="btn">Ingresar</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <div class="back-link">
            <a href="/">← Volver al sitio</a>
        </div>
    </div>
</body>
</html>
''',

    'admin_dashboard.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .admin-header {
            background: var(--secondary-color);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .admin-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .admin-logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .admin-nav-links {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .admin-nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
            white-space: nowrap;
        }
        
        .admin-nav-links a:hover {
            background: #373737;
        }
        
        .admin-container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .stat-card {
            background: var(--secondary-color);
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #aaa;
        }
        
        .admin-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .action-card {
            background: var(--secondary-color);
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
        }
        
        .action-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }
        
        .action-title {
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .action-description {
            color: #aaa;
            margin-bottom: 1.5rem;
        }
        
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: var(--primary-color);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #cc0000;
        }
        
        .export-import {
            background: var(--secondary-color);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .export-import h2 {
            margin-bottom: 1.5rem;
            color: var(--text-color);
        }
        
        .export-import-actions {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .file-input {
            background: #373737;
            padding: 0.75rem;
            border-radius: 5px;
            color: white;
        }
        
        .settings-preview {
            background: var(--secondary-color);
            padding: 1.5rem;
            border-radius: 10px;
        }
        
        .settings-preview h3 {
            margin-bottom: 1rem;
            color: var(--primary-color);
        }
        
        .settings-list {
            list-style: none;
        }
        
        .settings-list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #373737;
        }
        
        .settings-list li:last-child {
            border-bottom: none;
        }
        
        @media (max-width: 768px) {
            .admin-nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            .admin-nav-links {
                justify-content: center;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .admin-actions {
                grid-template-columns: 1fr;
            }
            
            .export-import-actions {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="admin-header">
        <nav class="admin-nav">
            <div class="admin-logo">VC7Day Admin</div>
            <div class="admin-nav-links">
                <a href="/admin/categories">Categorías</a>
                <a href="/admin/playlists">Playlists</a>
                <a href="/admin/videos">Videos</a>
                <a href="/admin/settings">Configuración</a>
                <a href="/admin/logout">Cerrar Sesión</a>
                <a href="/">Ver Sitio</a>
            </div>
        </nav>
    </header>

    <div class="admin-container">
        <h1>Dashboard de Administración</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-film"></i>
                </div>
                <div class="stat-number">{{ videos|length }}</div>
                <div class="stat-label">Total de Videos</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-folder"></i>
                </div>
                <div class="stat-number">{{ categories|length }}</div>
                <div class="stat-label">Categorías</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-list"></i>
                </div>
                <div class="stat-number">{{ playlists|length }}</div>
                <div class="stat-label">Playlists</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-eye"></i>
                </div>
                <div class="stat-number">{{ videos|sum(attribute='views') }}</div>
                <div class="stat-label">Vistas Totales</div>
            </div>
        </div>

        <div class="admin-actions">
            <div class="action-card">
                <div class="action-icon">
                    <i class="fas fa-folder-plus"></i>
                </div>
                <h3 class="action-title">Gestionar Categorías</h3>
                <p class="action-description">Crea, edita y elimina categorías para organizar tus videos</p>
                <a href="/admin/categories" class="btn">Administrar Categorías</a>
            </div>
            
            <div class="action-card">
                <div class="action-icon">
                    <i class="fas fa-list"></i>
                </div>
                <h3 class="action-title">Gestionar Playlists</h3>
                <p class="action-description">Crea y organiza playlists para agrupar videos relacionados</p>
                <a href="/admin/playlists" class="btn">Administrar Playlists</a>
            </div>
            
            <div class="action-card">
                <div class="action-icon">
                    <i class="fas fa-video"></i>
                </div>
                <h3 class="action-title">Gestionar Videos</h3>
                <p class="action-description">Agrega, edita y elimina videos en tu plataforma</p>
                <a href="/admin/videos" class="btn">Administrar Videos</a>
            </div>
            
            <div class="action-card">
                <div class="action-icon">
                    <i class="fas fa-cogs"></i>
                </div>
                <h3 class="action-title">Configuración</h3>
                <p class="action-description">Configura videos relacionados y otras opciones del sistema</p>
                <a href="/admin/settings" class="btn">Configurar Sistema</a>
            </div>
        </div>

        <div class="export-import">
            <h2>Exportar e Importar Datos</h2>
            <div class="export-import-actions">
                <a href="/admin/export" class="btn" download="vc7day_data.json">
                    <i class="fas fa-download"></i> Exportar Datos
                </a>
                <form action="/admin/import" method="POST" enctype="multipart/form-data" style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                    <input type="file" name="file" accept=".json" required class="file-input">
                    <button type="submit" class="btn">
                        <i class="fas fa-upload"></i> Importar Datos
                    </button>
                </form>
            </div>
        </div>

        <div class="settings-preview">
            <h3>Configuración Actual de Videos Relacionados</h3>
            <ul class="settings-list">
                <li><strong>Máximo de videos relacionados:</strong> {{ settings.related_videos_count }}</li>
                <li><strong>Relacionados automáticos:</strong> {{ "Activado" if settings.auto_related else "Desactivado" }}</li>
                <li><strong>Estrategia por defecto:</strong> 
                    {% if settings.default_related_strategy == 'category' %}
                    Misma categoría
                    {% elif settings.default_related_strategy == 'recent' %}
                    Más recientes
                    {% else %}
                    Más populares
                    {% endif %}
                </li>
            </ul>
        </div>
    </div>
</body>
</html>
''',

    'admin_settings.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuración - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .admin-header {
            background: var(--secondary-color);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .admin-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .admin-logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .admin-nav-links {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .admin-nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
            white-space: nowrap;
        }
        
        .admin-nav-links a:hover {
            background: #373737;
        }
        
        .admin-container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }
        
        .page-title {
            margin-bottom: 2rem;
            color: var(--text-color);
        }
        
        .settings-card {
            background: var(--secondary-color);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        input, select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #373737;
            border-radius: 5px;
            font-size: 1rem;
            background: #0f0f0f;
            color: var(--text-color);
            max-width: 300px;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .checkbox-group input {
            width: auto;
        }
        
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: var(--primary-color);
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #cc0000;
        }
        
        .info-box {
            background: #1a1a1a;
            padding: 1rem;
            border-radius: 5px;
            margin-top: 1rem;
            border-left: 4px solid var(--primary-color);
        }
        
        .info-box h4 {
            margin-bottom: 0.5rem;
            color: var(--primary-color);
        }
        
        .info-box ul {
            margin-left: 1.5rem;
            color: #aaa;
        }
        
        .info-box li {
            margin-bottom: 0.25rem;
        }
        
        @media (max-width: 768px) {
            .admin-nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            input, select {
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <header class="admin-header">
        <nav class="admin-nav">
            <div class="admin-logo">VC7Day Admin</div>
            <div class="admin-nav-links">
                <a href="/admin">Dashboard</a>
                <a href="/admin/categories">Categorías</a>
                <a href="/admin/playlists">Playlists</a>
                <a href="/admin/videos">Videos</a>
                <a href="/admin/logout">Cerrar Sesión</a>
                <a href="/">Ver Sitio</a>
            </div>
        </nav>
    </header>

    <div class="admin-container">
        <h1 class="page-title">Configuración del Sistema</h1>
        
        <div class="settings-card">
            <h2>Configuración de Videos Relacionados</h2>
            <form action="/admin/settings" method="POST">
                <div class="form-group">
                    <label for="related_videos_count">Número máximo de videos relacionados:</label>
                    <input type="number" id="related_videos_count" name="related_videos_count" 
                           value="{{ settings.related_videos_count }}" min="1" max="20" required>
                </div>
                
                <div class="form-group">
                    <div class="checkbox-group">
                        <input type="checkbox" id="auto_related" name="auto_related" 
                               {{ 'checked' if settings.auto_related }}>
                        <label for="auto_related">Activar videos relacionados automáticos</label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="default_related_strategy">Estrategia de relacionados automáticos:</label>
                    <select id="default_related_strategy" name="default_related_strategy" required>
                        <option value="category" {{ 'selected' if settings.default_related_strategy == 'category' }}>Misma categoría</option>
                        <option value="recent" {{ 'selected' if settings.default_related_strategy == 'recent' }}>Más recientes</option>
                        <option value="popular" {{ 'selected' if settings.default_related_strategy == 'popular' }}>Más populares</option>
                    </select>
                </div>
                
                <button type="submit" class="btn">Guardar Configuración</button>
            </form>
            
            <div class="info-box">
                <h4>Información sobre videos relacionados:</h4>
                <ul>
                    <li><strong>Máximo de videos:</strong> Controla cuántos videos relacionados se muestran como máximo</li>
                    <li><strong>Relacionados automáticos:</strong> Cuando está activado, el sistema completa automáticamente los videos relacionados si no hay suficientes configurados manualmente</li>
                    <li><strong>Estrategias:</strong>
                        <ul>
                            <li><strong>Misma categoría:</strong> Muestra videos de la misma categoría</li>
                            <li><strong>Más recientes:</strong> Muestra los videos más recientes</li>
                            <li><strong>Más populares:</strong> Muestra los videos con más vistas</li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
        
        <div class="settings-card">
            <h2>Gestión de Videos Relacionados Manuales</h2>
            <p>Para configurar videos relacionados manualmente para un video específico:</p>
            <ol style="margin-left: 1.5rem; color: #aaa; margin-bottom: 1rem;">
                <li>Ve a la sección "Gestionar Videos"</li>
                <li>Haz clic en el botón "Editar" del video que quieres configurar</li>
                <li>En el campo "Videos Relacionados", ingresa los IDs separados por comas</li>
                <li>Guarda los cambios</li>
            </ol>
            <a href="/admin/videos" class="btn">
                <i class="fas fa-video"></i> Gestionar Videos
            </a>
        </div>
    </div>
</body>
</html>
''',

    'admin_edit_video.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Video - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .admin-header {
            background: var(--secondary-color);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .admin-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .admin-logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .admin-nav-links {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .admin-nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
            white-space: nowrap;
        }
        
        .admin-nav-links a:hover {
            background: #373737;
        }
        
        .admin-container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }
        
        .page-title {
            margin-bottom: 2rem;
            color: var(--text-color);
        }
        
        .form-card {
            background: var(--secondary-color);
            padding: 2rem;
            border-radius: 10px;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #373737;
            border-radius: 5px;
            font-size: 1rem;
            background: #0f0f0f;
            color: var(--text-color);
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: var(--primary-color);
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
            margin-right: 1rem;
        }
        
        .btn:hover {
            background: #cc0000;
        }
        
        .btn-secondary {
            background: #6c757d;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .related-videos-preview {
            background: #1a1a1a;
            padding: 1rem;
            border-radius: 5px;
            margin-top: 0.5rem;
        }
        
        .related-video-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            border-bottom: 1px solid #373737;
        }
        
        .related-video-item:last-child {
            border-bottom: none;
        }
        
        .video-search {
            position: relative;
        }
        
        .search-results {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #0f0f0f;
            border: 1px solid #373737;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 100;
            display: none;
        }
        
        .search-result {
            padding: 0.75rem;
            cursor: pointer;
            border-bottom: 1px solid #373737;
        }
        
        .search-result:hover {
            background: #373737;
        }
        
        .search-result:last-child {
            border-bottom: none;
        }
        
        .info-text {
            color: #aaa;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }
        
        .current-related {
            margin-top: 1rem;
        }
        
        @media (max-width: 768px) {
            .admin-nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            .btn {
                margin-bottom: 1rem;
            }
        }
    </style>
</head>
<body>
    <header class="admin-header">
        <nav class="admin-nav">
            <div class="admin-logo">VC7Day Admin</div>
            <div class="admin-nav-links">
                <a href="/admin">Dashboard</a>
                <a href="/admin/categories">Categorías</a>
                <a href="/admin/playlists">Playlists</a>
                <a href="/admin/videos">Videos</a>
                <a href="/admin/settings">Configuración</a>
                <a href="/admin/logout">Cerrar Sesión</a>
                <a href="/">Ver Sitio</a>
            </div>
        </nav>
    </header>

    <div class="admin-container">
        <h1 class="page-title">Editar Video: {{ video.title }}</h1>
        
        <div class="form-card">
            <form action="/admin/videos/edit/{{ video.id }}" method="POST">
                <div class="form-group">
                    <label for="title">Título del Video:</label>
                    <input type="text" id="title" name="title" value="{{ video.title }}" required>
                </div>
                
                <div class="form-group">
                    <label for="description">Descripción:</label>
                    <textarea id="description" name="description" required>{{ video.description }}</textarea>
                </div>
                
                <div class="form-group">
                    <label for="video_url">URL del Video (.mp4):</label>
                    <input type="url" id="video_url" name="video_url" value="{{ video.video_url }}" required>
                </div>
                
                <div class="form-group">
                    <label for="thumbnail">URL del Thumbnail:</label>
                    <input type="url" id="thumbnail" name="thumbnail" value="{{ video.thumbnail }}" required>
                </div>
                
                <div class="form-group">
                    <label for="category_id">Categoría:</label>
                    <select id="category_id" name="category_id" required>
                        <option value="">Selecciona una categoría</option>
                        {% for category in categories %}
                        <option value="{{ category.id }}" {{ 'selected' if category.id == video.category_id }}>
                            {{ category.icon }} {{ category.name }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="playlist_id">Playlist (opcional):</label>
                    <select id="playlist_id" name="playlist_id">
                        <option value="None">Sin playlist</option>
                        {% for playlist in playlists %}
                        <option value="{{ playlist.id }}" {{ 'selected' if playlist.id == video.playlist_id }}>
                            {{ playlist.name }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="related_videos">Videos Relacionados (IDs separados por comas):</label>
                    <input type="text" id="related_videos" name="related_videos" 
                           value="{{ video.related_videos|join(', ') if video.related_videos }}" 
                           placeholder="Ej: 2, 5, 8">
                    <div class="info-text">
                        Ingresa los IDs de los videos relacionados separados por comas. 
                        <a href="#" id="openSearch">Buscar videos</a>
                    </div>
                    
                    <div class="video-search">
                        <input type="text" id="videoSearch" placeholder="Buscar videos..." style="display: none;">
                        <div class="search-results" id="searchResults"></div>
                    </div>
                </div>
                
                {% if related_videos_info %}
                <div class="current-related">
                    <h4>Videos relacionados actuales:</h4>
                    <div class="related-videos-preview">
                        {% for related in related_videos_info %}
                        <div class="related-video-item">
                            <span>#{{ related.id }} - {{ related.title }}</span>
                            <a href="/video/{{ related.id }}" target="_blank">Ver</a>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
                
                <div class="form-group">
                    <button type="submit" class="btn">Guardar Cambios</button>
                    <a href="/admin/videos" class="btn btn-secondary">Cancelar</a>
                </div>
            </form>
        </div>
    </div>

    <script>
        document.getElementById('openSearch').addEventListener('click', function(e) {
            e.preventDefault();
            const searchInput = document.getElementById('videoSearch');
            searchInput.style.display = 'block';
            searchInput.focus();
        });
        
        document.getElementById('videoSearch').addEventListener('input', function(e) {
            const query = e.target.value;
            const resultsContainer = document.getElementById('searchResults');
            
            if (query.length < 2) {
                resultsContainer.style.display = 'none';
                return;
            }
            
            fetch(`/api/videos/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(videos => {
                    resultsContainer.innerHTML = '';
                    
                    if (videos.length === 0) {
                        resultsContainer.innerHTML = '<div class="search-result">No se encontraron videos</div>';
                    } else {
                        videos.forEach(video => {
                            const result = document.createElement('div');
                            result.className = 'search-result';
                            result.textContent = `#${video.id} - ${video.title}`;
                            result.addEventListener('click', () => {
                                addVideoToRelated(video.id);
                                resultsContainer.style.display = 'none';
                                e.target.value = '';
                                e.target.style.display = 'none';
                            });
                            resultsContainer.appendChild(result);
                        });
                    }
                    
                    resultsContainer.style.display = 'block';
                });
        });
        
        function addVideoToRelated(videoId) {
            const relatedInput = document.getElementById('related_videos');
            const currentValue = relatedInput.value.trim();
            const currentIds = currentValue ? currentValue.split(',').map(id => id.trim()) : [];
            
            if (!currentIds.includes(videoId.toString())) {
                if (currentValue) {
                    relatedInput.value = currentValue + ', ' + videoId;
                } else {
                    relatedInput.value = videoId;
                }
            }
        }
        
        // Cerrar resultados al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.video-search')) {
                document.getElementById('searchResults').style.display = 'none';
            }
        });
    </script>
</body>
</html>
''',

    'admin_videos.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestionar Videos - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .admin-header {
            background: var(--secondary-color);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .admin-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .admin-logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .admin-nav-links {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .admin-nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
            white-space: nowrap;
        }
        
        .admin-nav-links a:hover {
            background: #373737;
        }
        
        .admin-container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }
        
        .page-title {
            margin-bottom: 2rem;
            color: var(--text-color);
        }
        
        .admin-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 2rem;
        }
        
        .form-card, .list-card {
            background: var(--secondary-color);
            padding: 2rem;
            border-radius: 10px;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #373737;
            border-radius: 5px;
            font-size: 1rem;
            background: #0f0f0f;
            color: var(--text-color);
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: var(--primary-color);
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #cc0000;
        }
        
        .btn-danger {
            background: #dc3545;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .btn-sm {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
        
        .btn-edit {
            background: #28a745;
        }
        
        .btn-edit:hover {
            background: #218838;
        }
        
        .videos-list {
            list-style: none;
        }
        
        .video-item {
            padding: 1.5rem;
            border-bottom: 1px solid #373737;
            transition: background 0.3s;
        }
        
        .video-item:hover {
            background: #373737;
        }
        
        .video-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .video-title {
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }
        
        .video-category {
            background: var(--primary-color);
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-size: 0.8rem;
            display: inline-block;
            margin-right: 0.5rem;
        }
        
        .video-playlist {
            background: #28a745;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-size: 0.8rem;
            display: inline-block;
        }
        
        .video-description {
            color: #aaa;
            margin-bottom: 1rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.4;
        }
        
        .video-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .video-url {
            font-size: 0.8rem;
            color: #888;
            word-break: break-all;
            flex: 1;
        }
        
        .video-actions {
            display: flex;
            gap: 0.5rem;
            flex-shrink: 0;
        }
        
        .empty-state {
            text-align: center;
            color: #aaa;
            padding: 2rem;
        }
        
        .related-count {
            background: #28a745;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-size: 0.8rem;
            margin-left: 0.5rem;
        }
        
        @media (max-width: 768px) {
            .admin-content {
                grid-template-columns: 1fr;
            }
            
            .admin-nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            .video-header {
                flex-direction: column;
            }
            
            .video-footer {
                flex-direction: column;
                align-items: start;
            }
            
            .video-actions {
                width: 100%;
                justify-content: space-between;
            }
        }
    </style>
</head>
<body>
    <header class="admin-header">
        <nav class="admin-nav">
            <div class="admin-logo">VC7Day Admin</div>
            <div class="admin-nav-links">
                <a href="/admin">Dashboard</a>
                <a href="/admin/categories">Categorías</a>
                <a href="/admin/playlists">Playlists</a>
                <a href="/admin/settings">Configuración</a>
                <a href="/admin/logout">Cerrar Sesión</a>
                <a href="/">Ver Sitio</a>
            </div>
        </nav>
    </header>

    <div class="admin-container">
        <h1 class="page-title">Gestionar Videos</h1>
        
        <div class="admin-content">
            <!-- Formulario para agregar video -->
            <div class="form-card">
                <h2>Agregar Nuevo Video</h2>
                <form action="/admin/videos/add" method="POST">
                    <div class="form-group">
                        <label for="title">Título del Video:</label>
                        <input type="text" id="title" name="title" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="description">Descripción:</label>
                        <textarea id="description" name="description" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="video_url">URL del Video (.mp4):</label>
                        <input type="url" id="video_url" name="video_url" required placeholder="https://ejemplo.com/video.mp4">
                    </div>
                    
                    <div class="form-group">
                        <label for="thumbnail">URL del Thumbnail:</label>
                        <input type="url" id="thumbnail" name="thumbnail" required placeholder="https://ejemplo.com/thumb.jpg">
                    </div>
                    
                    <div class="form-group">
                        <label for="category_id">Categoría:</label>
                        <select id="category_id" name="category_id" required>
                            <option value="">Selecciona una categoría</option>
                            {% for category in categories %}
                            <option value="{{ category.id }}">{{ category.icon }} {{ category.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="playlist_id">Playlist (opcional):</label>
                        <select id="playlist_id" name="playlist_id">
                            <option value="None">Sin playlist</option>
                            {% for playlist in playlists %}
                            <option value="{{ playlist.id }}">{{ playlist.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="related_videos">Videos Relacionados (IDs separados por comas):</label>
                        <input type="text" id="related_videos" name="related_videos" placeholder="Ej: 2, 5, 8">
                    </div>
                    
                    <button type="submit" class="btn">Agregar Video</button>
                </form>
            </div>

            <!-- Lista de videos -->
            <div class="list-card">
                <h2>Videos Existentes</h2>
                {% if videos %}
                <ul class="videos-list">
                    {% for video in videos %}
                    <li class="video-item">
                        <div class="video-header">
                            <div style="flex: 1;">
                                <div class="video-title">{{ video.title }}</div>
                                <div>
                                    <span class="video-category">{{ video.category_name }}</span>
                                    {% if video.playlist_name != 'Sin playlist' %}
                                    <span class="video-playlist">{{ video.playlist_name }}</span>
                                    {% endif %}
                                    {% if video.related_videos %}
                                    <span class="related-count">{{ video.related_videos|length }} relacionados</span>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        
                        <div class="video-description">{{ video.description }}</div>
                        
                        <div class="video-footer">
                            <div class="video-url">
                                <strong>Vistas:</strong> {{ video.views }} | 
                                <strong>Likes:</strong> {{ video.likes }}<br>
                                <strong>Video:</strong> {{ video.video_url[:50] }}...<br>
                                <strong>Thumb:</strong> {{ video.thumbnail[:50] }}...
                            </div>
                            <div class="video-actions">
                                <a href="/video/{{ video.id }}" class="btn btn-sm" target="_blank">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="/admin/videos/edit/{{ video.id }}" class="btn btn-edit btn-sm">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="/admin/videos/delete/{{ video.id }}" class="btn btn-danger btn-sm" onclick="return confirm('¿Estás seguro de que quieres eliminar este video?')">
                                    <i class="fas fa-trash"></i>
                                </a>
                            </div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
                {% else %}
                <div class="empty-state">
                    <p>No hay videos agregados aún.</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
''',

    'admin_categories.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestionar Categorías - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .admin-header {
            background: var(--secondary-color);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .admin-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .admin-logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .admin-nav-links {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .admin-nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
            white-space: nowrap;
        }
        
        .admin-nav-links a:hover {
            background: #373737;
        }
        
        .admin-container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }
        
        .page-title {
            margin-bottom: 2rem;
            color: var(--text-color);
        }
        
        .admin-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 2rem;
        }
        
        .form-card, .list-card {
            background: var(--secondary-color);
            padding: 2rem;
            border-radius: 10px;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        input, select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #373737;
            border-radius: 5px;
            font-size: 1rem;
            background: #0f0f0f;
            color: var(--text-color);
        }
        
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: var(--primary-color);
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #cc0000;
        }
        
        .btn-danger {
            background: #dc3545;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .categories-list {
            list-style: none;
        }
        
        .category-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid #373737;
            transition: background 0.3s;
        }
        
        .category-item:hover {
            background: #373737;
        }
        
        .category-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .category-icon {
            font-size: 1.5rem;
        }
        
        .category-name {
            font-weight: 500;
        }
        
        .category-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .empty-state {
            text-align: center;
            color: #aaa;
            padding: 2rem;
        }
        
        @media (max-width: 768px) {
            .admin-content {
                grid-template-columns: 1fr;
            }
            
            .admin-nav {
                flex-direction: column;
                gap: 1rem;
            }
        }
    </style>
</head>
<body>
    <header class="admin-header">
        <nav class="admin-nav">
            <div class="admin-logo">VC7Day Admin</div>
            <div class="admin-nav-links">
                <a href="/admin">Dashboard</a>
                <a href="/admin/playlists">Playlists</a>
                <a href="/admin/videos">Videos</a>
                <a href="/admin/settings">Configuración</a>
                <a href="/admin/logout">Cerrar Sesión</a>
                <a href="/">Ver Sitio</a>
            </div>
        </nav>
    </header>

    <div class="admin-container">
        <h1 class="page-title">Gestionar Categorías</h1>
        
        <div class="admin-content">
            <!-- Formulario para agregar categoría -->
            <div class="form-card">
                <h2>Agregar Nueva Categoría</h2>
                <form action="/admin/categories/add" method="POST">
                    <div class="form-group">
                        <label for="name">Nombre de la Categoría:</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="icon">Icono (Emoji):</label>
                        <input type="text" id="icon" name="icon" required placeholder="🎬">
                        <small style="color: #aaa;">Ingresa un emoji como icono</small>
                    </div>
                    
                    <button type="submit" class="btn">Agregar Categoría</button>
                </form>
            </div>

            <!-- Lista de categorías -->
            <div class="list-card">
                <h2>Categorías Existentes</h2>
                {% if categories %}
                <ul class="categories-list">
                    {% for category in categories %}
                    <li class="category-item">
                        <div class="category-info">
                            <span class="category-icon">{{ category.icon }}</span>
                            <span class="category-name">{{ category.name }}</span>
                        </div>
                        <div class="category-actions">
                            <a href="/admin/categories/delete/{{ category.id }}" class="btn btn-danger" onclick="return confirm('¿Estás seguro de que quieres eliminar esta categoría?')">
                                <i class="fas fa-trash"></i>
                            </a>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
                {% else %}
                <div class="empty-state">
                    <p>No hay categorías creadas aún.</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
''',

    'admin_playlists.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestionar Playlists - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .admin-header {
            background: var(--secondary-color);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .admin-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .admin-logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .admin-nav-links {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .admin-nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
            white-space: nowrap;
        }
        
        .admin-nav-links a:hover {
            background: #373737;
        }
        
        .admin-container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }
        
        .page-title {
            margin-bottom: 2rem;
            color: var(--text-color);
        }
        
        .admin-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 2rem;
        }
        
        .form-card, .list-card {
            background: var(--secondary-color);
            padding: 2rem;
            border-radius: 10px;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #373737;
            border-radius: 5px;
            font-size: 1rem;
            background: #0f0f0f;
            color: var(--text-color);
        }
        
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: var(--primary-color);
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #cc0000;
        }
        
        .btn-danger {
            background: #dc3545;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .btn-sm {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
        
        .btn-edit {
            background: #28a745;
        }
        
        .btn-edit:hover {
            background: #218838;
        }
        
        .playlists-list {
            list-style: none;
        }
        
        .playlist-item {
            padding: 1.5rem;
            border-bottom: 1px solid #373737;
            transition: background 0.3s;
        }
        
        .playlist-item:hover {
            background: #373737;
        }
        
        .playlist-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .playlist-title {
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }
        
        .playlist-category {
            background: var(--primary-color);
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-size: 0.8rem;
            display: inline-block;
        }
        
        .playlist-description {
            color: #aaa;
            margin-bottom: 1rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.4;
        }
        
        .playlist-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .playlist-meta {
            font-size: 0.8rem;
            color: #888;
        }
        
        .playlist-actions {
            display: flex;
            gap: 0.5rem;
            flex-shrink: 0;
        }
        
        .empty-state {
            text-align: center;
            color: #aaa;
            padding: 2rem;
        }
        
        .video-search {
            position: relative;
        }
        
        .search-results {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #0f0f0f;
            border: 1px solid #373737;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 100;
            display: none;
        }
        
        .search-result {
            padding: 0.75rem;
            cursor: pointer;
            border-bottom: 1px solid #373737;
        }
        
        .search-result:hover {
            background: #373737;
        }
        
        .search-result:last-child {
            border-bottom: none;
        }
        
        .info-text {
            color: #aaa;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }
        
        @media (max-width: 768px) {
            .admin-content {
                grid-template-columns: 1fr;
            }
            
            .admin-nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            .playlist-header {
                flex-direction: column;
            }
            
            .playlist-footer {
                flex-direction: column;
                align-items: start;
            }
            
            .playlist-actions {
                width: 100%;
                justify-content: space-between;
            }
        }
    </style>
</head>
<body>
    <header class="admin-header">
        <nav class="admin-nav">
            <div class="admin-logo">VC7Day Admin</div>
            <div class="admin-nav-links">
                <a href="/admin">Dashboard</a>
                <a href="/admin/categories">Categorías</a>
                <a href="/admin/videos">Videos</a>
                <a href="/admin/settings">Configuración</a>
                <a href="/admin/logout">Cerrar Sesión</a>
                <a href="/">Ver Sitio</a>
            </div>
        </nav>
    </header>

    <div class="admin-container">
        <h1 class="page-title">Gestionar Playlists</h1>
        
        <div class="admin-content">
            <!-- Formulario para agregar playlist -->
            <div class="form-card">
                <h2>Agregar Nueva Playlist</h2>
                <form action="/admin/playlists/add" method="POST">
                    <div class="form-group">
                        <label for="name">Nombre de la Playlist:</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="description">Descripción:</label>
                        <textarea id="description" name="description" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="category_id">Categoría:</label>
                        <select id="category_id" name="category_id" required>
                            <option value="">Selecciona una categoría</option>
                            {% for category in categories %}
                            <option value="{{ category.id }}">{{ category.icon }} {{ category.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="thumbnail">URL del Thumbnail:</label>
                        <input type="url" id="thumbnail" name="thumbnail" required placeholder="https://ejemplo.com/thumb.jpg">
                    </div>
                    
                    <div class="form-group">
                        <label for="videos">Videos (IDs separados por comas):</label>
                        <input type="text" id="videos" name="videos" placeholder="Ej: 1, 2, 3">
                        <div class="info-text">
                            Ingresa los IDs de los videos separados por comas. 
                            <a href="#" id="openSearch">Buscar videos</a>
                        </div>
                        
                        <div class="video-search">
                            <input type="text" id="videoSearch" placeholder="Buscar videos..." style="display: none;">
                            <div class="search-results" id="searchResults"></div>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn">Agregar Playlist</button>
                </form>
            </div>

            <!-- Lista de playlists -->
            <div class="list-card">
                <h2>Playlists Existentes</h2>
                {% if playlists %}
                <ul class="playlists-list">
                    {% for playlist in playlists %}
                    <li class="playlist-item">
                        <div class="playlist-header">
                            <div style="flex: 1;">
                                <div class="playlist-title">{{ playlist.name }}</div>
                                <span class="playlist-category">{{ playlist.category_name }}</span>
                            </div>
                        </div>
                        
                        <div class="playlist-description">{{ playlist.description }}</div>
                        
                        <div class="playlist-footer">
                            <div class="playlist-meta">
                                <strong>{{ playlist.videos_count }} videos</strong><br>
                                {% if playlist.first_video %}
                                Primer video: {{ playlist.first_video.title[:50] }}...
                                {% endif %}
                            </div>
                            <div class="playlist-actions">
                                <a href="/playlist/{{ playlist.id }}" class="btn btn-sm" target="_blank">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="/admin/playlists/edit/{{ playlist.id }}" class="btn btn-edit btn-sm">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="/admin/playlists/delete/{{ playlist.id }}" class="btn btn-danger btn-sm" onclick="return confirm('¿Estás seguro de que quieres eliminar esta playlist?')">
                                    <i class="fas fa-trash"></i>
                                </a>
                            </div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
                {% else %}
                <div class="empty-state">
                    <p>No hay playlists creadas aún.</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <script>
        document.getElementById('openSearch').addEventListener('click', function(e) {
            e.preventDefault();
            const searchInput = document.getElementById('videoSearch');
            searchInput.style.display = 'block';
            searchInput.focus();
        });
        
        document.getElementById('videoSearch').addEventListener('input', function(e) {
            const query = e.target.value;
            const resultsContainer = document.getElementById('searchResults');
            
            if (query.length < 2) {
                resultsContainer.style.display = 'none';
                return;
            }
            
            fetch(`/api/videos/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(videos => {
                    resultsContainer.innerHTML = '';
                    
                    if (videos.length === 0) {
                        resultsContainer.innerHTML = '<div class="search-result">No se encontraron videos</div>';
                    } else {
                        videos.forEach(video => {
                            const result = document.createElement('div');
                            result.className = 'search-result';
                            result.textContent = `#${video.id} - ${video.title}`;
                            result.addEventListener('click', () => {
                                addVideoToPlaylist(video.id);
                                resultsContainer.style.display = 'none';
                                e.target.value = '';
                                e.target.style.display = 'none';
                            });
                            resultsContainer.appendChild(result);
                        });
                    }
                    
                    resultsContainer.style.display = 'block';
                });
        });
        
        function addVideoToPlaylist(videoId) {
            const videosInput = document.getElementById('videos');
            const currentValue = videosInput.value.trim();
            const currentIds = currentValue ? currentValue.split(',').map(id => id.trim()) : [];
            
            if (!currentIds.includes(videoId.toString())) {
                if (currentValue) {
                    videosInput.value = currentValue + ', ' + videoId;
                } else {
                    videosInput.value = videoId;
                }
            }
        }
        
        // Cerrar resultados al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.video-search')) {
                document.getElementById('searchResults').style.display = 'none';
            }
        });
    </script>
</body>
</html>
''',

    'admin_edit_playlist.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Playlist - VC7Day</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff0000;
            --secondary-color: #282828;
            --background-color: #0f0f0f;
            --text-color: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .admin-header {
            background: var(--secondary-color);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .admin-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .admin-logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .admin-nav-links {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .admin-nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
            white-space: nowrap;
        }
        
        .admin-nav-links a:hover {
            background: #373737;
        }
        
        .admin-container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }
        
        .page-title {
            margin-bottom: 2rem;
            color: var(--text-color);
        }
        
        .form-card {
            background: var(--secondary-color);
            padding: 2rem;
            border-radius: 10px;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #373737;
            border-radius: 5px;
            font-size: 1rem;
            background: #0f0f0f;
            color: var(--text-color);
        }
        
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: var(--primary-color);
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
            margin-right: 1rem;
        }
        
        .btn:hover {
            background: #cc0000;
        }
        
        .btn-secondary {
            background: #6c757d;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .videos-preview {
            background: #1a1a1a;
            padding: 1rem;
            border-radius: 5px;
            margin-top: 0.5rem;
        }
        
        .video-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            border-bottom: 1px solid #373737;
        }
        
        .video-item:last-child {
            border-bottom: none;
        }
        
        .video-search {
            position: relative;
        }
        
        .search-results {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #0f0f0f;
            border: 1px solid #373737;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 100;
            display: none;
        }
        
        .search-result {
            padding: 0.75rem;
            cursor: pointer;
            border-bottom: 1px solid #373737;
        }
        
        .search-result:hover {
            background: #373737;
        }
        
        .search-result:last-child {
            border-bottom: none;
        }
        
        .info-text {
            color: #aaa;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }
        
        .current-videos {
            margin-top: 1rem;
        }
        
        @media (max-width: 768px) {
            .admin-nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            .btn {
                margin-bottom: 1rem;
            }
        }
    </style>
</head>
<body>
    <header class="admin-header">
        <nav class="admin-nav">
            <div class="admin-logo">VC7Day Admin</div>
            <div class="admin-nav-links">
                <a href="/admin">Dashboard</a>
                <a href="/admin/categories">Categorías</a>
                <a href="/admin/playlists">Playlists</a>
                <a href="/admin/videos">Videos</a>
                <a href="/admin/settings">Configuración</a>
                <a href="/admin/logout">Cerrar Sesión</a>
                <a href="/">Ver Sitio</a>
            </div>
        </nav>
    </header>

    <div class="admin-container">
        <h1 class="page-title">Editar Playlist: {{ playlist.name }}</h1>
        
        <div class="form-card">
            <form action="/admin/playlists/edit/{{ playlist.id }}" method="POST">
                <div class="form-group">
                    <label for="name">Nombre de la Playlist:</label>
                    <input type="text" id="name" name="name" value="{{ playlist.name }}" required>
                </div>
                
                <div class="form-group">
                    <label for="description">Descripción:</label>
                    <textarea id="description" name="description" required>{{ playlist.description }}</textarea>
                </div>
                
                <div class="form-group">
                    <label for="category_id">Categoría:</label>
                    <select id="category_id" name="category_id" required>
                        <option value="">Selecciona una categoría</option>
                        {% for category in categories %}
                        <option value="{{ category.id }}" {{ 'selected' if category.id == playlist.category_id }}>
                            {{ category.icon }} {{ category.name }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="thumbnail">URL del Thumbnail:</label>
                    <input type="url" id="thumbnail" name="thumbnail" value="{{ playlist.thumbnail }}" required>
                </div>
                
                <div class="form-group">
                    <label for="videos">Videos (IDs separados por comas):</label>
                    <input type="text" id="videos" name="videos" 
                           value="{{ playlist.videos|join(', ') if playlist.videos }}" 
                           placeholder="Ej: 1, 2, 3">
                    <div class="info-text">
                        Ingresa los IDs de los videos separados por comas. 
                        <a href="#" id="openSearch">Buscar videos</a>
                    </div>
                    
                    <div class="video-search">
                        <input type="text" id="videoSearch" placeholder="Buscar videos..." style="display: none;">
                        <div class="search-results" id="searchResults"></div>
                    </div>
                </div>
                
                {% if playlist_videos_info %}
                <div class="current-videos">
                    <h4>Videos en la playlist:</h4>
                    <div class="videos-preview">
                        {% for video in playlist_videos_info %}
                        <div class="video-item">
                            <span>#{{ video.id }} - {{ video.title }}</span>
                            <a href="/video/{{ video.id }}" target="_blank">Ver</a>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
                
                <div class="form-group">
                    <button type="submit" class="btn">Guardar Cambios</button>
                    <a href="/admin/playlists" class="btn btn-secondary">Cancelar</a>
                </div>
            </form>
        </div>
    </div>

    <script>
        document.getElementById('openSearch').addEventListener('click', function(e) {
            e.preventDefault();
            const searchInput = document.getElementById('videoSearch');
            searchInput.style.display = 'block';
            searchInput.focus();
        });
        
        document.getElementById('videoSearch').addEventListener('input', function(e) {
            const query = e.target.value;
            const resultsContainer = document.getElementById('searchResults');
            
            if (query.length < 2) {
                resultsContainer.style.display = 'none';
                return;
            }
            
            fetch(`/api/videos/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(videos => {
                    resultsContainer.innerHTML = '';
                    
                    if (videos.length === 0) {
                        resultsContainer.innerHTML = '<div class="search-result">No se encontraron videos</div>';
                    } else {
                        videos.forEach(video => {
                            const result = document.createElement('div');
                            result.className = 'search-result';
                            result.textContent = `#${video.id} - ${video.title}`;
                            result.addEventListener('click', () => {
                                addVideoToPlaylist(video.id);
                                resultsContainer.style.display = 'none';
                                e.target.value = '';
                                e.target.style.display = 'none';
                            });
                            resultsContainer.appendChild(result);
                        });
                    }
                    
                    resultsContainer.style.display = 'block';
                });
        });
        
        function addVideoToPlaylist(videoId) {
            const videosInput = document.getElementById('videos');
            const currentValue = videosInput.value.trim();
            const currentIds = currentValue ? currentValue.split(',').map(id => id.trim()) : [];
            
            if (!currentIds.includes(videoId.toString())) {
                if (currentValue) {
                    videosInput.value = currentValue + ', ' + videoId;
                } else {
                    videosInput.value = videoId;
                }
            }
        }
        
        // Cerrar resultados al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.video-search')) {
                document.getElementById('searchResults').style.display = 'none';
            }
        });
    </script>
</body>
</html>
'''
}

# Sobrescribir la función render_template para usar templates embebidos
import flask
original_render_template = flask.render_template

def render_template(template_name, **context):
    if template_name in templates:
        return flask.render_template_string(templates[template_name], **context)
    return original_render_template(template_name, **context)

# Asignar la función personalizada
app.jinja_env.globals.update(render_template=render_template)

# Inicializar la aplicación
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

init_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)