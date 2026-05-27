def choose_move(observation):
    obs = observation if isinstance(observation, dict) else {}
    w = obs.get('grid_width', 0)
    h = obs.get('grid_height', 0)
    sx, sy = obs.get('self_position', (0, 0))
    ox, oy = obs.get('opponent_position', (0, 0))
    res = obs.get('resources', [])
    blocks = set(map(tuple, obs.get('obstacles', []) or []))

    dx = 0
    dy = 0

    # Try to move toward closest resource if available
    best = None
    if isinstance(res, list) and res:
        for r in res:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                if 0 <= rx < w and 0 <= ry < h:
                    d = abs(rx - sx) + abs(ry - sy)
                    if best is None or d < best[0]:
                        best = (d, rx, ry)
        if best:
            rx, ry = best[1], best[2]
            if rx > sx:
                dx = 1
            elif rx < sx:
                dx = -1
            if rx == sx:
                if ry > sy:
                    dy = 1
                elif ry < sy:
                    dy = -1

    # If no movement yet, head toward center to stay robust
    if dx == 0 and dy == 0:
        cx = max(0, min(w - 1, w // 2))
        cy = max(0, min(h - 1, h // 2))
        if cx > sx:
            dx = 1
        elif cx < sx:
            dx = -1
        if cy > sy:
            dy = 1
        elif cy < sy:
            dy = -1

    # Generate candidate moves and pick first that is valid and not hitting obstacles
    cand = [(dx, dy), (0, 0), (-dx, 0), (0, -dy), (dx, 0), (0, dy), (-dx, 0), (0, -dy)]
    seen = set()
    for tx, ty in cand:
        if (tx, ty) in seen:
            continue
        seen.add((tx, ty))
        nx, ny = sx + tx, sy + ty
        if tx in (-1, 0, 1) and ty in (-1, 0, 1):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocks:
                dx, dy = tx, ty
                break

    if dx not in (-1, 0, 1):
        dx = 0
    if dy not in (-1, 0, 1):
        dy = 0

    return [dx, dy]
