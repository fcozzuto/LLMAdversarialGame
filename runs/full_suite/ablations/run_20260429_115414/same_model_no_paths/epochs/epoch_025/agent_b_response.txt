def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_r = None
        best_val = None
        # Choose a resource where we are relatively closer than the opponent.
        # Value: (my_dist - opp_dist) with small bias to closer absolute distance.
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            val = (ds - do) * 10 + ds
            if best_val is None or val < best_val:
                best_val = val
                best_r = (rx, ry)

        tx, ty = best_r
        # Move one step toward target, but also discourage stepping closer to opponent.
        best_move = None
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            ns = dist(nx, ny, tx, ty)
            no = dist(nx, ny, ox, oy)
            # Prefer reducing distance to target; if tie, prefer being farther from opponent.
            score = ns * 1000 - no
            # Extra: don't step onto target if opponent is already there next turn-like? keep simple.
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])] if best_move is not None else [0, 0]

    # No visible resources: head to a stable hotspot near our side of the map while avoiding obstacles/opponent.
    # Deterministic fallback: choose step minimizing (dist to preferred corner-side + proximity to opponent).
    preferred = (0, 0) if sx + sy <= (w - 1 - sx) + (h - 1 - sy) else (w - 1, h - 1)
    px, py = preferred
    best_move = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = dist(nx, ny, px, py) * 1000 + dist(nx, ny, ox, oy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])] if best_move is not None else [0, 0]