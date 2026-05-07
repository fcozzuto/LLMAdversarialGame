def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_move = (0, 0)

    opp_pos = (ox, oy)
    turns = int(observation.get("turns_remaining", 0) or 0)
    turn_bias = 0.0
    if turns > 0:
        turn_bias = 1.0 / (turns + 1)

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate immediate move by how favorable it is to be first to a resource.
        # Primary: maximize (opp_reach - self_reach); Secondary: minimize self_reach; Tertiary: minimize distance to nearest resource.
        best_local = None
        for rx, ry in resources:
            sd = king_dist(nx, ny, rx, ry)
            od = king_dist(opp_pos[0], opp_pos[1], rx, ry)
            # If we can reach in same/less time, it should dominate. We add small deterministic preference for earlier capture.
            val = (od - sd, -sd, -(1.0 + sd) * turn_bias)
            if best_local is None or val > best_local:
                best_local = val

        if best_local is None:
            continue

        if best is None or best_local > best:
            best = best_local
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]