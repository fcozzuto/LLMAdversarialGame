def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    if resources:
        # Score moves by deterministic "race" to a resource where we can be strictly closer than opponent.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            opp_pen = 0
            # Prefer moves that increase distance from opponent unless it helps grab a resource.
            dop_now = cheb(sx, sy, ox, oy)
            dop_next = cheb(nx, ny, ox, oy)
            if dop_next <= dop_now:
                opp_pen = 0.4 * (dop_now - dop_next + 1)
            v = -0.05 * (abs(nx - ox) + abs(ny - oy)) - opp_pen

            # Race each resource: larger margin (oppdist - selfdist) is better.
            # Also reward approaching some reachable resource.
            top_margin = -10**9
            top_selfdist = 10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                margin = do - ds
                if margin > top_margin or (margin == top_margin and ds < top_selfdist):
                    top_margin = margin
                    top_selfdist = ds
            # Convert margin to value; positive margin dominates.
            if top_margin > 0:
                v += 3.0 * top_margin - 0.12 * top_selfdist
            else:
                v += 0.15 * top_margin - 0.06 * top_selfdist

            # Tie-break: prefer staying closer to resources (lower best dist) and within bounds already.
            if v > bestv:
                bestv = v
                best = (dx, dy)
    else:
        # No visible resources: keep distance from opponent while drifting toward center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dcen = cheb(nx, ny, cx, cy)
            dop = cheb(nx, ny, ox, oy)
            dnow = cheb(sx, sy, ox, oy)
            v = -0.9 * dcen + 0.55 * dop
            if dop < dnow:
                v -= 0.6 * (dnow - dop + 1)
            if v > bestv:
                bestv = v
                best = (dx, dy)

    return [int(best[0]), int(best[1])]