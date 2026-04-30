def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def clamp(x, y):
        if x < 0: x = 0
        if y < 0: y = 0
        if x >= w: x = w - 1
        if y >= h: y = h - 1
        return x, y
    def dist(a, b):
        return (a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1])

    # If no resources, just move toward center while keeping away from opponent.
    if not resources:
        cx, cy = (w-1)//2, (h-1)//2
        best = (None, -10**18)
        for dx, dy in deltas:
            nx, ny = clamp(sx+dx, sy+dy)
            if (nx, ny) in obstacles:
                continue
            myd = dist((nx, ny), (cx, cy))
            oppd = dist((nx, ny), (ox, oy))
            score = -myd + 0.25 * oppd
            if score > best[1]:
                best = ((dx, dy), score)
        return list(best[0] if best[0] is not None else (0, 0))

    # Pick target that we can reach first, biased to resources where opponent is relatively farther.
    best_target = None
    best_val = -10**18
    for r in resources:
        myd = dist((sx, sy), r)
        opd = dist((ox, oy), r)
        # Encourage advantage: (opponent distance - my distance), and prefer nearer resources.
        val = (opd - myd) - 0.3 * myd
        if val > best_val:
            best_val = val
            best_target = r

    tx, ty = best_target
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = clamp(sx+dx, sy+dy)
        if (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), (tx, ty))
        # Avoid giving opponent a quick approach: maximize separation after move.
        oppd = dist((nx, ny), (ox, oy))
        # If opponent is nearer to target than us, try to increase separation more than distance.
        my_now = dist((sx, sy), (tx, ty))
        opp_now = dist((ox, oy), (tx, ty))
        lead = 1 if opp_now - my_now > 0 else -1
        score = -myd + 0.55 * oppd + (0.15 * lead * (opp_now - my_now))
        # Small preference for staying on board and not moving into tight spots near obstacles.
        if dx != 0 or dy != 0:
            near_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    px, py = nx+ax, ny+ay
                    if px < 0 or py < 0 or px >= w or py >= h:
                        continue
                    if (px, py) in obstacles:
                        near_obs += 1
            score -= 0.08 * near_obs
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]