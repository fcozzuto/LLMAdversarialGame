def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
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

    # If opponent is close to a resource, deprioritize it; otherwise prioritize where we are closer.
    best_r = None
    best_v = None
    for r in resources:
        dm = dist8((sx, sy), r)
        do = dist8((ox, oy), r)
        avoid = 1 if r[1] == oy else 0  # counter sweep_rows: avoid opponent row
        # Main value: prefer (do - dm) i.e., resources we can reach earlier, and avoid opponent row.
        v = (do - dm, 1 - avoid, -dm, -abs(r[0] - sx), -abs(r[1] - sy), r[0], r[1])
        if best_v is None or v > best_v:
            best_v, best_r = v, r

    tx, ty = best_r

    # Choose a move that decreases distance to target; break ties by avoiding opponent row collisions.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                nm = dist8((nx, ny), (tx, ty))
                op_row_pen = 1 if ny == oy else 0
                # Also lightly avoid moving into opponent's exact square.
                hit_pen = 1 if (nx, ny) == (ox, oy) else 0
                # Prefer keeping within-board and making progress.
                score = (-nm, -op_row_pen, -hit_pen, -abs(nx - tx), -abs(ny - ty), -abs(dx) - abs(dy))
                moves.append((score, [dx, dy]))

    moves.sort(key=lambda t: t[0], reverse=True)
    return moves[0][1] if moves else [0, 0]