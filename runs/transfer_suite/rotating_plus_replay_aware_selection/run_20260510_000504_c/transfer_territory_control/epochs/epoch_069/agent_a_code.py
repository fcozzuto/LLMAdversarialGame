def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    if resources:
        tx, ty = resources[0]
        target = (int(tx), int(ty))
    else:
        frontier = []
        flip_candidates = []
        for (x, y) in (self_terr if self_terr else [(sx, sy)]):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: continue
                    nx, ny = x + dx, y + dy
                    if not inb(nx, ny) or (nx, ny) in obstacles: continue
                    if (nx, ny) in unclaimed: frontier.append((nx, ny))
                    elif (nx, ny) in opp_terr: flip_candidates.append((nx, ny))
        if frontier:
            target = min(frontier, key=lambda p: (dist((sx, sy), p), abs(p[0] - cx) + abs(p[1] - cy)) )
        elif flip_candidates:
            target = min(flip_candidates, key=lambda p: (dist((sx, sy), p), -dist((cx, cy), p)) )
        else:
            # fallback: go toward center or any boundary cell
            candidates = list(opp_terr)[:64]
            if not candidates:
                candidates = list(unclaimed)[:64]
            if candidates:
                target = min(candidates, key=lambda p: (dist((sx, sy), p), abs(p[0] - cx) + abs(p[1] - cy)))
            else:
                target = (int(round(cx)), int(round(cy)))

    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            cell = (nx, ny)
            score = 0
            if cell in self_terr: score += 5
            if cell in unclaimed: score += 12
            if cell in opp_terr: score += 40  # flipping on entry
            # steer toward target and center; also keep away from obstacles by mild penalty
            score += 30 - (dist((nx, ny), target) ** 0.5)
            score += -0.5 * (abs(nx - cx) + abs(ny - cy))
            # prefer moves that immediately expand frontier: adjacent unclaimed count
            adj_unclaimed = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0: continue
                    x2, y2 = nx + ax, ny + ay
                    if inb(x2, y2) and (x2, y2) in unclaimed:
                        adj_unclaimed += 1
            score += 3 * adj_unclaimed
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move