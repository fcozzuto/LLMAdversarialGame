def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Choose a target resource that maximizes our lead; then pick the move that improves that lead.
    # Scoring: lead improvement + resource priority (closer overall).
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inside(nx, ny):
            continue
        move_val = -10**18
        for rx, ry in resources:
            d_me_before = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            d_me_after = cheb(nx, ny, rx, ry)

            lead_before = d_opp - d_me_before
            lead_after = d_opp - d_me_after
            lead_improve = lead_after - lead_before

            # Prefer targets we can reach no later than opponent; tie-break by shorter absolute distance.
            reach_bias = 0
            if d_me_after <= d_opp:
                reach_bias = 5
            priority = -(d_me_after + 0.15 * d_opp)

            v = lead_improve * 3 + reach_bias + priority

            # Small deterministic obstacle avoidance: prefer moves that reduce distance from next cell to nearest obstacle cell
            # (without path search) to keep movement inside open space.
            if obs:
                od = 10**9
                for obx, oby in obs:
                    dd = cheb(nx, ny, obx, oby)
                    if dd < od:
                        od = dd
                v += 0.05 * od

            if v > move_val:
                move_val = v

        # Break ties deterministically: prefer staying still only if strictly best; otherwise prefer moves with lexicographically smaller delta.
        if move_val > best_val or (move_val == best_val and (mx, my) < best_move):
            best_val = move_val
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]