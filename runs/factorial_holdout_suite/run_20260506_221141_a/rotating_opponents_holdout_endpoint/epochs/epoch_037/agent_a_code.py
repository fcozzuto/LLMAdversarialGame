def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my_turns = int(observation.get("turns_remaining", 0) or 0)
    risk_gain = 2 if my_turns < 20 else 1

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_mv = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate the best resource to race for from the resulting position
        best_cell = None
        best_cell_val = None
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer winning races (opp_dist - self_dist). Encourage near-term gains.
            cell_val = (do - dm) * risk_gain - dm * 0.05
            if best_cell_val is None or cell_val > best_cell_val:
                best_cell_val = cell_val
                best_cell = (rx, ry)

        # Deterministic tie-break: prefer closer resource then lexicographic move
        if best_cell is None:
            continue
        if best_val is None:
            best_val = (best_cell_val, -cheb(nx, ny, best_cell[0], best_cell[1]), dx, dy)
            best_mv = (dx, dy)
        else:
            cand = (best_cell_val, -cheb(nx, ny, best_cell[0], best_cell[1]), dx, dy)
            if cand > best_val:
                best_val = cand
                best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]