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

    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = (-(10**18), 0, 0)
    # Stronger than before: evaluate move by maximal advantage over all resources,
    # and add an "edge pressure" term to counter edge_patrol tendency.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        # Distance to opponent from new position (avoid giving chase opportunities)
        opp_from_me = manh(nx, ny, ox, oy)

        # Reward being closer to a resource than the opponent.
        # Advantage = opp_dist - my_dist (bigger is better).
        best_adv_for_move = -(10**18)
        best_self_d = 10**9
        for rx, ry in resources:
            my_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            adv = opp_d - my_d
            # Small tie-break: prefer shorter my_d
            if adv > best_adv_for_move or (adv == best_adv_for_move and my_d < best_self_d):
                best_adv_for_move = adv
                best_self_d = my_d

        # Edge pressure: prefer moving away from interior when opponent is near edges,
        # but still allow resource advantage to dominate.
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
        edge_term = (2.0 if edge <= 1 else 0.0) * (1.0 if (min(ox, oy, w - 1 - ox, h - 1 - oy) <= 1) else -0.2)

        # If we can capture immediately (standing on resource), dominate.
        on_resource = 1.0 if (nx, ny) in obs.union(set(resources)) and (nx, ny) in set(resources) else 0.0

        val = (best_adv_for_move * 10.0) + (-opp_from_me * 0.15) + edge_term + (on_resource * 100.0)
        if val > best[0]:
            best = (val, dx, dy)

    # Fallback: deterministic safe move toward any resource
    if best[1] == 0 and best[2] == 0:
        rx, ry = min(resources, key=lambda r: manh(sx, sy, r[0], r[1]))
        dx = 0 if rx == sx else (1 if rx > sx else -1)
        dy = 0 if ry == sy else (1 if ry > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    return [int(best[1]), int(best[2])]