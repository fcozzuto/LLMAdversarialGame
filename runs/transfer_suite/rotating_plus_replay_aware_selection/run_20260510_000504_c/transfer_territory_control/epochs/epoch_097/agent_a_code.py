def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    my_name = observation.get("self_name", "agent_a")
    op_name = observation.get("opponent_name", "agent_b")
    scores = observation.get("scores") or {}
    my_score = float(scores.get(my_name, 0.0) or 0.0)
    op_score = float(scores.get(op_name, 0.0) or 0.0)
    aggressive = my_score < op_score

    best = None
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if (nx, ny) in opp_terr:
            base = 8.0
        elif (nx, ny) in unclaimed:
            base = 3.5
        elif (nx, ny) in self_terr:
            base = 1.0
        else:
            base = 2.0

        my_d = man(nx, ny, ox, oy)
        op_d = man(ox, oy, nx, ny)
        # (op_d == my_d) but keep structure deterministic; use neighbor/frontier bias instead.
        # Penalize moving away from opponent-nearfrontier when aggressive.
        # Find if this move is adjacent to my territory (frontier expansion).
        neigh = [(nx + ddx, ny + ddy) for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1)]]
        adj_my = any((tx, ty) in self_terr for tx, ty in neigh if inb(tx, ty))
        adj_opp = any((tx, ty) in opp_terr for tx, ty in neigh if inb(tx, ty))
        frontier_bonus = 1.8 if adj_my else 0.0
        contest_bonus = 2.2 if adj_opp else 0.0

        # Encourage grabbing nearest unclaimed when not aggressive.
        if not aggressive:
            target_list = list(unclaimed)[:30]
            if target_list:
                # deterministic nearest by (manhattan, x, y)
                tx, ty = min(target_list, key=lambda p: (abs(p[0] - nx) + abs(p[1] - ny), p[0], p[1]))
                dist_pen = 0.04 * (abs(tx - nx) + abs(ty - ny))
            else:
                dist_pen = 0.0
        else:
            dist_pen = 0.0

        # Avoid locking into obstacle-adjacent corridors by discouraging cells with many nearby obstacles.
        obs_near = 0
        for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            tx, ty = nx + ddx, ny + ddy
            if not inb(tx, ty) or (tx, ty) in obstacles:
                obs_near += 1
        obst_pen = 0.08 * obs_near

        val = base + frontier_bonus + contest_bonus - dist_pen - obst_pen
        if (best is None) or (val > best_val) or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]