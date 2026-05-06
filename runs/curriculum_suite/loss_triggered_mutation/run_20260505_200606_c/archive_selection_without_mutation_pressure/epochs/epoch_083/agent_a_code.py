def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    res = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = p[0], p[1]
            if (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_dx, best_dy = 0, 0
    best_key = None

    # Opponent archetype: nearest-resource. Approximate their progress by -1 on manhattan distance each turn.
    opp_progress = 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Defense: prefer moves that keep distance from opponent if we can't secure a resource.
        opp_sep = man(nx, ny, ox, oy)

        # Targeting: choose the resource where we are more likely to beat them to pickup.
        # Reward securing resources, penalize giving opponent a faster grab.
        best_for_move = -10**18
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry) - opp_progress
            # Beat condition: we arrive in fewer steps than their next-turn-approximated arrival.
            if sd < od:
                val = 200000 - 1000 * sd + 10 * (od - sd)
            else:
                val = -200000 + 200 * (sd - od)  # strongly discourage losing resources
            # Secondary bias: slightly prefer nearer contested resources.
            val -= sd
            if val > best_for_move:
                best_for_move = val

        # If all resources are bad, fall back to maximizing separation and staying toward resources.
        # Key makes decisions deterministic and non-redundant.
        key = (-(best_for_move + opp_sep * 5), sd_min := min(man(nx, ny, rx, ry) for rx, ry in res), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]