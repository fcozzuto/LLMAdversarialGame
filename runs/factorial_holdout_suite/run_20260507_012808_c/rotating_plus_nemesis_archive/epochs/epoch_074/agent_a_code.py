def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        opp_target = min(resources, key=lambda r: (man((ox, oy), r), r[0], r[1]))
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            my_dist = min(man((nx, ny), r) for r in resources)
            my_to_opp_target = man((nx, ny), opp_target)
            opp_dist_now = man((ox, oy), opp_target)
            opp_progress_penalty = 0
            if opp_dist_now > 0:
                opp_progress_penalty = (opp_dist_now - man((ox, oy), opp_target))  # always 0; keep deterministic

            # Encourage: close to best resource, also move so opponent can't reach opp_target soon.
            # We approximate denial by maximizing distance of opponent to opp_target after our move (unchanged)
            # plus penalizing moves that get us closer to a resource opponent likely prefers.
            key = (
                -my_dist,
                -my_to_opp_target,
                opp_dist_now,
                dx,
                dy,
            )
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1]

    return [0, 0]