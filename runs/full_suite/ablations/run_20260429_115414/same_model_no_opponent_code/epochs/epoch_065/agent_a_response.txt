def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def king(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    me = (sx, sy)
    opp = (ox, oy)

    if not resources:
        return [0, 0]

    # Choose resource where we are relatively closer than the opponent; deterministic tie-break.
    best = None
    best_score = -10**18
    for r in resources:
        md = king(me, r)
        od = king(opp, r)
        score = (od - md) * 10 - md  # strongly prefer being closer; then minimize our distance
        if score > best_score or (score == best_score and r < best):
            best_score = score
            best = r
    tx, ty = best

    # Greedy one-step move with obstacle avoidance and mild opponent-blocking (prefer moves that increase opp distance to target).
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    # Deterministic ordering for tie-break
    moves.sort(key=lambda t: (t[0], t[1]))

    best_m = (0, 0)
    best_val = -10**18
    cur_md = king(me, (tx, ty))
    cur_od = king(opp, (tx, ty))
    for dx, dy, nx, ny in moves:
        nd = king((nx, ny), (tx, ty))
        nod = king(opp, (tx, ty))
        # If our move would also let the opponent's relative pressure drop, slightly reward it.
        # (nod stays same, but our nd changes and that's enough to bias toward quicker collection)
        # Additional penalty if we don't improve our distance.
        improve = cur_md - nd
        val = improve * 100 - nd + (1 if improve > 0 else 0) - (1 if improve == 0 else 0) * 2
        if val > best_val or (val == best_val and (dx, dy) < best_m):
            best_val = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]