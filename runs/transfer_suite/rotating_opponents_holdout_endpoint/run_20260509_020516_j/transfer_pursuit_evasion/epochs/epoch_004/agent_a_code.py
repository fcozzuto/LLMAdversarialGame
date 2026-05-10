def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles", [])
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or (("evad" in opp_role) and ("evad" not in self_role))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors(x, y):
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs_set:
                out.append((nx, ny))
        return out

    def bfs_dist(start, goal, max_nodes=64):
        if start == goal:
            return 0
        if not in_bounds(goal[0], goal[1]) or goal in obs_set:
            return 10**9
        sx0, sy0 = start
        q = [(sx0, sy0)]
        dist = {(sx0, sy0): 0}
        i = 0
        while i < len(q) and len(dist) < max_nodes:
            x, y = q[i]; i += 1
            d = dist[(x, y)]
            for nx, ny in neighbors(x, y):
                if (nx, ny) not in dist:
                    nd = d + 1
                    if (nx, ny) == goal:
                        return nd
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return 10**9

    corners = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
    if pursuer:
        target = (ox, oy)
        best_val = 10**9
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                nx, ny = sx, sy
            d = bfs_dist((nx, ny), target)
            val = d
            if val < best_val or (val == best_val and (dx, dy) < best_move):
                best_val, best_move = val, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # Evader: pick a corner that is hardest for pursuer to reach (maximize distance from opponent via BFS)
        opp = (ox, oy)
        corner_scores = []
        for c in corners:
            ds = bfs_dist(opp, c)
            corner_scores.append((ds, c))
        corner_scores.sort(key=lambda t: (-t[0], t[1][0], t[1][1]))
        target_corner = corner_scores[0][1]

        # Then choose move that maximizes distance to opponent while still heading toward target_corner
        best_val = -10**9
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                nx, ny = sx, sy
            d_opp = bfs_dist((nx, ny), opp)
            d_goal = bfs_dist((nx, ny), target_corner)
            # primary: farther from opponent; secondary: closer to chosen escape corner
            val = d_opp * 100 - d_goal
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val, best_move = val, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]