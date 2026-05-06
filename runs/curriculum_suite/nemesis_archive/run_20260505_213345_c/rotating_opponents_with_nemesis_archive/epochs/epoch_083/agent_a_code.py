def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Prefer resources where we can get there first; if close, avoid opponent row overlap a bit.
    best = None
    best_val = None
    for r in resources:
        dm = dist8((sx, sy), r)
        do = dist8((ox, oy), r)
        # If we're substantially closer, very strong; if equal, favor further from opponent row.
        row_pen = 0 if r[1] != oy else 2
        val = (do - dm, -row_pen, -dm, -(r[0] + r[1]) % 2, r[0], r[1])
        if best is None or val > best_val:
            best = r
            best_val = val

    tx, ty = best

    # Interception nudge: if opponent is closer or tied, bias toward a point that blocks their approach line.
    d_best_dm = dist8((sx, sy), best)
    d_best_do = dist8((ox, oy), best)
    if d_best_do <= d_best_dm:
        # Pick a target on/near the segment from opponent to the resource (one step closer to resource).
        vx = best[0] - ox
        vy = best[1] - oy
        step_x = 0 if vx == 0 else (1 if vx > 0 else -1)
        step_y = 0 if vy == 0 else (1 if vy > 0 else -1)
        ix, iy = ox + step_x, oy + step_y
        if 0 <= ix < w and 0 <= iy < h and (ix, iy) not in obstacles:
            # Only switch if it doesn't move us too far off our chosen resource.
            if dist8((sx, sy), (ix, iy)) <= d_best_dm + 1:
                tx, ty = ix, iy

    # Choose legal move that minimizes distance to (tx, ty); deterministic tie-break.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Tie-break order: prefer closer, then keep x smaller, then y smaller.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist8((nx, ny), (tx, ty))
        score = (d, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]