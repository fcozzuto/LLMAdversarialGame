def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = [tuple(r) for r in (observation.get("resources") or []) if isinstance(r, (list, tuple)) and len(r) == 2]
    obstacles = [tuple(o) for o in (observation.get("obstacles") or []) if isinstance(o, (list, tuple)) and len(o) == 2]
    obs = set(obstacles)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    closest_res_for = lambda px, py: min(resources, key=lambda r: manh(px, py, r[0], r[1]))

    # Approximate opponent next move by greedy toward their closest resource
    opp_target = closest_res_for(ox, oy)
    best_opp = (ox, oy)
    best_opp_d = 10**9
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        d = manh(nx, ny, opp_target[0], opp_target[1])
        if d < best_opp_d:
            best_opp_d = d
            best_opp = (nx, ny)
    nx_opp, ny_opp = best_opp

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        for rx, ry in resources:
            our_d = manh(nx, ny, rx, ry)
            opp_d = manh(nx_opp, ny_opp, rx, ry)
            lead = opp_d - our_d  # positive => we are closer than opponent next
            can_reach = (our_d <= opp_d)
            target_bonus = 7 if (rx, ry) == opp_target else 0
            val = max(val, lead * 12 - our_d + target_bonus + (20 if can_reach else 0))

        # Small preference for moves that improve distance to opponent's current closest resource
        if manh(nx, ny, opp_target[0], opp_target[1]) < manh(sx, sy, opp_target[0], opp_target[1]):
            val += 2

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]