def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            cell = (int(r[0]), int(r[1]))
            if cell not in obstacles:
                resources.append(cell)
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Sort deterministically: prefer resources closer to opponent last (deny), then by coordinates
    resources_sorted = sorted(resources, key=lambda rc: (cheb(ox, oy, rc[0], rc[1]), rc[0], rc[1]))

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose resource that maximizes "we arrive first" margin after this move
        # score = (opp_dist - self_dist) + small tie-break for self_dist
        local_best = -10**18
        for rx, ry in resources_sorted[:min(10, len(resources_sorted))]:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - self_d
            val = margin * 100 - self_d
            if val > local_best:
                local_best = val
        # Prefer moves that improve the best achievable margin; tie-break lex
        if local_best > best_val or (local_best == best_val and (dx, dy) < best_move):
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]