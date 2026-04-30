def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        # No resources: try to approach opponent to limit their options
        best = [0, 0]
        bd = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    d = max(abs(nx - ox), abs(ny - oy))
                    if d > bd:
                        bd = d
                        best = [dx, dy]
        return best

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a resource where we are relatively closer than the opponent
    best_res = None
    best_key = None  # lower better
    for r in resources:
        rr = tuple(r)
        ds = dist((sx, sy), rr)
        do = dist((ox, oy), rr)
        # Key: prefer resources we can reach earlier; break ties by larger advantage
        key = (ds, - (do - ds), rr[0], rr[1])
        if best_key is None or key < best_key:
            best_key = key
            best_res = rr

    tx, ty = best_res
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        our_d = max(abs(nx - tx), abs(ny - ty))
        opp_d = max(abs(nx - ox), abs(ny - oy))
        # Prefer decreasing distance to target; then keep away from opponent
        val = (our_d, -opp_d, (nx - tx), (ny - ty), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]