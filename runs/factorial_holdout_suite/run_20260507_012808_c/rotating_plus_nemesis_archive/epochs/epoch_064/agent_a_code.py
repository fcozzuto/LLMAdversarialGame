def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        # Head roughly away from opponent to limit denials
        dx = -1 if sx > (w - 1 - ox) else (1 if sx < (w - 1 - ox) else 0)
        dy = -1 if sy > (h - 1 - oy) else (1 if sy < (h - 1 - oy) else 0)
        return [int(max(-1, min(1, dx))), int(max(-1, min(1, dy)))]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose target that we are closest to, but also discourages targets the opponent is likely to reach first.
    best_t = None
    best_v = None
    for tx, ty in resources:
        myd = manh(sx, sy, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # Value: minimize myd; discourage when opponent is closer (resource_denier archetype)
        v = (myd, myd - (opd * 0.6), tx, ty)
        if best_v is None or v < best_v:
            best_v = v
            best_t = (tx, ty)

    tx, ty = best_t

    best_move = (10**18, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moving onto a resource (immediate collection)
        on_res = 1 if (nx, ny) in resources else 0
        d = manh(nx, ny, tx, ty)
        # Tie-break towards lower dx/dy lexicographically for determinism
        key = (-on_res, d, dx, dy, nx, ny)
        if key < best_move[0:1] or best_move[1] is None:
            best_move = (key[0], (dx, dy), key)

    return best_move[1] if best_move[1] is not None else [0, 0]