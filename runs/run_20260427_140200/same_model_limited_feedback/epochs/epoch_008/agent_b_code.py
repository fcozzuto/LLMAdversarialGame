def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    def clamp(x, a, b):
        return a if x < a else (b if x > b else x)

    def d2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy

    if not resources:
        # No resources: just move to increase distance from opponent deterministically
        best = (None, -10**18)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            nx, ny = clamp(nx, 0, w-1), clamp(ny, 0, h-1)
            if (nx, ny) in obstacles:
                continue
            score = d2(nx, ny, ox, oy)
            if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
                best = ((dx, dy), score)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w-1), clamp(ny, 0, h-1)
        if (nx, ny) in obstacles:
            continue

        best_adv = -10**18
        best_dist_self = 10**18
        best_dist_opp = 10**18
        for rx, ry in resources:
            ds = d2(nx, ny, rx, ry)
            do = d2(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer than opponent to this resource
            if adv > best_adv:
                best_adv, best_dist_self, best_dist_opp = adv, ds, do
            elif adv == best_adv:
                if ds < best_dist_self:
                    best_dist_self, best_dist_opp = ds, do
        # Prefer greater advantage; then be closer; then farther from opponent
        score = best_adv * 1000 - best_dist_self + best_dist_opp * 0.01 + d2(nx, ny, ox, oy) * 0.001
        candidates.append((score, dx, dy, best_adv, best_dist_self))

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    if not candidates:
        return [0, 0]
    _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]