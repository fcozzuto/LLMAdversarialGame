def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obs_set = set((x, y) for x, y in obstacles)
    def king_dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    parity = observation["turn_index"] & 1
    scored_resources = []
    for r in resources:
        if (r[0], r[1]) in obs_set:
            continue
        d_self = king_dist((sx, sy), (r[0], r[1]))
        d_opp = king_dist((ox, oy), (r[0], r[1]))
        reachable_win = 1 if d_self <= d_opp else 0
        if parity == 0:
            # push for uncontested/closest
            key = (0 if reachable_win else 1, d_self, d_opp)
        else:
            # change policy: if contested, go for those where we keep distance from opponent
            key = (0 if reachable_win else 1, d_self + (0 if reachable_win else 1) * (d_opp - d_self), -d_opp)
        scored_resources.append((key, r))
    if not scored_resources:
        # fallback: avoid obstacles while drifting away from opponent
        target = (0 if sx > w//2 else w-1, 0 if sy > h//2 else h-1)
    else:
        target = scored_resources[0][1]
    best = None
    best_val = -10**9
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        d_t = king_dist((nx, ny), (target[0], target[1]))
        d_o = king_dist((nx, ny), (ox, oy))
        # prefer taking target, staying safer, and not getting stuck near opponent early
        val = -d_t + 0.08 * d_o
        if (nx, ny) == (target[0], target[1]):
            val += 5.0
        if d_o == 0:
            val -= 2.0
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]