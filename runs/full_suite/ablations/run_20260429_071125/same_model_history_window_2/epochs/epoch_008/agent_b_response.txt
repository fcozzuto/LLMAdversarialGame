def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_resource_for(posx, posy):
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = md(posx, posy, rx, ry)
            if d < bestd:
                bestd = d
                best = (rx, ry)
        return best, bestd

    if not resources:
        # Deterministic: maximize distance from opponent while staying inside.
        best = (0, 0)
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = md(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    opp_pickable = set()
    for rx, ry in resources:
        for dx, dy in deltas:
            tx, ty = ox + dx, oy + dy
            if tx == rx and ty == ry and inside(tx, ty):
                opp_pickable.add((rx, ry))
    opp_can_pick = len(opp_pickable) > 0

    best_move = (0, 0)
    best_val = -10**18

    # Evaluate each move with advantage-to-resource and penalty if opponent can pick next while we don't.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # If we step onto a resource, prioritize it heavily.
        stepped = (nx, ny) in set((r[0], r[1]) for r in resources)
        val = 0
        if stepped:
            val += 100000

        # Resource advantage: for closest few resources, reward being nearer than opponent.
        adv_terms = 0
        for rx, ry in sorted(resources, key=lambda r: md(ox, oy, r[0], r[1]))[:6]:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer smaller distances; also prefer beating opponent (od - sd).
            if sd == 0:
                adv_terms += 1000
            else:
                adv_terms += (od - sd) * (20 / (1 + sd))
        val += adv_terms

        # Threat penalty: opponent can pick immediately and we don't land on any pickable resource ourselves.
        if opp_can_pick:
            if (nx, ny) not in opp_pickable:
                # If we are far from the opponent's nearest pickable, penalize more.
                nearest_threat_d = min(md(nx, ny, rx, ry) for rx, ry in opp_pickable)
                val -= 2000 + 50 * nearest_threat_d

        # Gentle tie-break: move that reduces distance to opponent's nearest resource overall.
        _, my_nearest = best_resource_for(nx, ny)
        _, opp_nearest = best_resource_for(ox, oy)
        val += 0.1 * (opp_nearest - my_nearest)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]