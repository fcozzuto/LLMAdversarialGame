def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = ax - bx, ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Target selection: pick a resource that we can reach no later than opponent (ideally),
    # then among them choose one with smallest self distance; otherwise choose one that minimizes (our_dist - opp_dist).
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        advantage = od - sd  # positive means we are closer
        reachable_flag = 1 if sd <= od else 0
        key = (reachable_flag, advantage, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t if best_t is not None else (w // 2, h // 2)

    # If we and opponent are both far from the target, bias toward blocking their best alternative by
    # steering toward squares that increase their minimum distance to any resource more than ours.
    any_res = bool(resources)
    consider_resources = resources if any_res else [(tx, ty)]

    best_m = (0, 0)
    best_s = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Core score: increase advantage at target
        sd_new = man((nx, ny), (tx, ty))
        od_new = man((ox, oy), (tx, ty))
        core = od_new - sd_new

        # Opponent pressure: compare their best resource distance before/after our move.
        # We can't move opponent, but our move can change whether they have contested options
        # (resources closer to them than us), by potentially letting us reach those first.
        min_opp_lead_before = None
        min_opp_lead_after = None
        for rx, ry in consider_resources:
            sd0 = man((sx, sy), (rx, ry))
            od0 = man((ox, oy), (rx, ry))
            lead0 = od0 - sd0
            sd1 = man((nx, ny), (rx, ry))
            od1 = od0
            lead1 = od1 - sd1
            # We care most about resources where opponent is leading (negative/low lead).
            cand0 = lead0
            cand1 = lead1
            if min_opp_lead_before is None or cand0 < min_opp_lead_before:
                min_opp_lead_before = cand0
            if min_opp_lead_after is None or cand1 < min_opp_lead_after:
                min_opp_lead_after = cand1

        pressure = 0
        if min_opp_lead_before is not None and min_opp_lead_after is not None:
            # Prefer moves that raise (reduce opponent lead severity) across resources.
            pressure = (min_opp_lead_after - min_opp_lead_before)

        # Safety: penalize moving closer to opponent if not improving target advantage.
        dist_opp_before = man((sx, sy), (ox, oy))
        dist_opp_after = man((nx, ny), (ox, oy))
        opp_closer = dist_opp_after - dist_opp_before  # negative is closer

        # Deterministic tie-break: prefer keeping x then y movement small in a fixed order
        tie = (abs(dx), abs(dy), dx, dy)

        score = (core * 1000) + (pressure) + (-opp_closer) + (-sd_new) - tie[0] * 0.01 - tie[1] * 0.02
        if best_s is None or score > best_s:
            best_s = score
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]