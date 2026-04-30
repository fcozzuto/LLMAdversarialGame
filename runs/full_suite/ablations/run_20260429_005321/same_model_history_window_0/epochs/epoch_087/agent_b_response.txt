def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    candidates = []
    if resources:
        best_res = None; best_adv = -10**9
        for r in resources:
            adv = dist((sx, sy), r) - dist((ox, oy), r)
            if adv < best_adv:
                best_adv = adv; best_res = r
        target = best_res if best_res is not None else resources[0]
        # We chose the resource where opponent is closer (adv small) -> invert to pick where we are closer:
        # Fix: re-pick maximizing (opp_dist - self_dist)
        best_res = None; best_gain = -10**9
        for r in resources:
            gain = dist((ox, oy), r) - dist((sx, sy), r)
            if gain > best_gain:
                best_gain = gain; best_res = r
        target = best_res
    else:
        target = None

    best_move = (0, 0); best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        if target is None:
            # No resources: drift away from opponent while moving toward center.
            cx, cy = (w - 1) / 2, (h - 1) / 2
            val = dist((nx, ny), (ox, oy)) - 0.1 * (abs(nx - cx) + abs(ny - cy))
        else:
            nd_to_target = dist((nx, ny), target)
            cur_to_target = dist((sx, sy), target)
            # Prefer reducing distance to target and staying away from opponent if contesting.
            opp_d = dist((nx, ny), (ox, oy))
            opp_cur_d = dist((sx, sy), (ox, oy))
            # If target is contested, slightly prefer moves that increase our lead.
            self_gain = (dist((ox, oy), target) - dist((nx, ny), target))
            opp_gain = (dist((nx, ny), target) - dist((ox, oy), target))
            val = (-nd_to_target) + 0.5 * (cur_to_target - nd_to_target) + 0.08 * opp_d + 0.6 * self_gain
            # If we're already closer than opponent to target, avoid giving up too much.
            if dist((sx, sy), target) <= dist((ox, oy), target):
                val += 0.2 * (opp_cur_d - opp_d)
            # Discourage stepping into immediate obstacle-neighbor traps.
            trap = 0
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    tx, ty = nx + ex, ny + ey
                    if (tx, ty) in obstacles:
                        trap += 1
            val -= 0.05 * trap
        if val > best_val:
            best_val = val; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]