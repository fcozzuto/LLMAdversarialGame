def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    best_move = None
    best_score = None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        # Greedy: maximize advantage after this move; slight preference for closer to "earliest" captures.
        best_r_local = None
        best_val_local = None
        for rx, ry in resources:
            ds = cheb(nsx, nsy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Advantage: bigger means we can reach sooner than opponent.
            val = (do - ds, -ds, -cheb(nsx, nsy, ox, oy), rx, ry)
            if best_val_local is None or val > best_val_local:
                best_val_local = val
                best_r_local = (rx, ry)
        # Tie-break between moves deterministically.
        rx, ry = best_r_local
        final_score = (best_val_local[0], best_val_local[1], best_val_local[2], -rx, -ry)
        if best_score is None or final_score > best_score:
            best_score = final_score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]