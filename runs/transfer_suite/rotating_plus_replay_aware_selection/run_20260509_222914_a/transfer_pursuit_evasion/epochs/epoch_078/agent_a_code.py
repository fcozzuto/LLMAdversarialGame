def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return False
        return (nx, ny) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score_after(nx, ny):
        d0 = dist(nx, ny, ox, oy)
        # wall avoidance: prefer having at least one open neighbor
        open_n = 0
        for dx, dy in moves:
            ax, ay = nx + dx, ny + dy
            if valid(ax, ay):
                open_n += 1
        # 2-ply: assume opponent moves greedily (deterministic by tie-break order)
        best_op = d0
        if not i_am_evader:
            # pursuer: opponent is evader; choose move that maximizes distance after its move
            best_op = -10**9
            for mdx, mdy in moves:
                px, py = ox + mdx, oy + mdy
                if valid(px, py):
                    dd = dist(nx, ny, px, py)
                    if dd > best_op:
                        best_op = dd
        else:
            # evader: opponent is pursuer; choose move that minimizes distance after its move
            best_op = 10**9
            for mdx, mdy in moves:
                px, py = ox + mdx, oy + mdy
                if valid(px, py):
                    dd = dist(nx, ny, px, py)
                    if dd < best_op:
                        best_op = dd
        # combine: pursuer wants small distance, evader wants large distance
        if i_am_evader:
            return (best_op * 1000) + (open_n * 3) - (d0 * 0.5)
        else:
            return (-best_op * 1000) + (open_n * 3) - (d0 * 0.5)

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score_after(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best