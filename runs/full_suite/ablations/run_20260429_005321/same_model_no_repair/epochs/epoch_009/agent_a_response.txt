def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obs = set((p[0], p[1]) for p in observation.get("obstacles", []) or [])
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs(start):
        if not inb(start[0], start[1]) or start in obs:
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
            nd = d + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obs and (nx, ny) not in dist:
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        tx = 1 if sx < w // 2 else -1 if sx > w // 2 else 0
        ty = 1 if sy < h // 2 else -1 if sy > h // 2 else 0
        return [tx, ty]

    opp_dist = bfs((ox, oy))
    if opp_dist is None:
        opp_dist = {}

    best_move = (0, 0)
    best_score = -10**9
    for mdx, mdy in deltas:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_dist = bfs((nx, ny))
        if self_dist is None:
            continue

        local_best = -10**9
        for rx, ry in resources:
            dS = self_dist.get((rx, ry))
            dO = opp_dist.get((rx, ry))
            if dS is None:
                continue
            if dO is None:
                gain = 100 - dS  # we can reach; opp can't
            else:
                gain = (dO - dS)  # positive if we arrive earlier
            # Prefer earlier/closer and also avoid giving opp too easy counter-capture
            score = gain * 10 - dS
            # small bias to slightly prioritize resources nearer to our side (top-left corner)
            score -= (rx + ry) * 0.05
            if score > local_best:
                local_best = score

        if local_best > best_score:
            best_score = local_best
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]