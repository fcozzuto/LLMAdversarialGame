def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs_dist(start):
        if start in obstacles:
            return None
        dist = {(start[0], start[1]): 0}
        q = [(start[0], start[1])]
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            d = dist[(x, y)]
            if d >= 20:
                continue
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                if (nx, ny) not in dist:
                    dist[(nx, ny)] = d + 1
                    q.append((nx, ny))
        return dist

    def value_target(rx, ry, d_self, d_opp):
        if d_self is None:
            return None
        # prefer taking before opponent; otherwise still aim for high reward and closeness
        if d_opp is None:
            lead = 1
        else:
            lead = d_opp - d_self  # positive if we arrive earlier
        score = 0
        score += (10000 if lead > 0 else (2000 if lead == 0 else 0))
        score += 10 * lead
        score += -(d_self or 0)
        # smaller tie-breaking toward upper-left to change policy deterministically
        score += -(rx + 0.01 * ry)
        # original resources coordinates sometimes imply value; use them lightly to break symmetry
        score += 0.001 * (rx * 7 + ry * 3)
        return score

    if not resources:
        return [0, 0]

    opp_dist = bfs_dist((ox, oy))

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_dist = bfs_dist((nx, ny))
        # choose the best target for this move (arrive-advantage-first heuristic)
        move_best = -10**18
        for rx, ry in resources:
            d_self = self_dist.get((rx, ry)) if self_dist is not None else None
            d_opp = opp_dist.get((rx, ry)) if opp_dist is not None else None
            sc = value_target(rx, ry, d_self, d_opp)
            if sc is not None and sc > move_best:
                move_best = sc
        # slight preference for staying mobile toward opponent direction to vary play
        move_best += 0.05 * (abs(ox - (nx)) + abs(oy - (ny)))
        if move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]