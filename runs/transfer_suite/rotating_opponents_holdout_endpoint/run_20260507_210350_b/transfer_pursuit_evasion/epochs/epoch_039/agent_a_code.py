def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        return dx if dx > dy else dy

    def valid(x, y):
        if not inb(x, y): return False
        return (x, y) not in obstacles

    def edge_bias(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    best = None
    best_key = None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not valid(nsx, nsy):
            continue
        # Predict evader response: choose their move that maximizes our separation after we move.
        best_sep = None
        for odx, ody in moves:
            nox, noy = ox + odx, oy + ody
            if not valid(nox, noy):
                nox, noy = ox, oy  # if invalid, deterministic engine would keep them in place
            sep = cheb(nsx, nsy, nox, noy)
            if best_sep is None or sep > best_sep:
                best_sep = sep
        # Primary: minimize predicted separation; Secondary: prefer closer to opponent's current position; Tertiary: avoid edges.
        key = (best_sep, cheb(nsx, nsy, ox, oy), -edge_bias(nsx, nsy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        # Fallback: move toward opponent by Chebyshev metric.
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]
    return best