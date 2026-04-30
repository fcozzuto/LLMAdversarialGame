def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal_moves(px, py):
        out = []
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) not in occ:
                out.append((dx, dy))
        if not out:
            return [(0, 0)]
        out.sort()
        return out

    def best_response_move(px, py, epx, epy):
        # maximize opponent->resource proximity advantage vs our position
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            best, bestv = (0, 0), -10**9
            for dx, dy in legal_moves(px, py):
                nx, ny = px + dx, py + dy
                v = -cheb(nx, ny, cx, cy)
                if v > bestv:
                    bestv, best = v, (dx, dy)
            return best
        best, bestv = (0, 0), -10**18
        for dx, dy in legal_moves(px, py):
            nx, ny = px + dx, py + dy
            # choose the single resource that gives opponent best lead vs us after this move
            cur = -10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(epx, epy, rx, ry)
                lead = opd - myd
                if lead > cur:
                    cur = lead
            if cur > bestv:
                bestv, best = cur, (dx, dy)
        return best

    def evaluate_after(my_pos, op_pos):
        mx, my = my_pos
        ex, ey = op_pos
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return -cheb(mx, my, cx, cy) - 0.01 * cheb(mx, my, ex, ey)
        # maximize my lead over resources; break ties by smaller my distance
        best = -10**18
        best_tie = 10**18
        for rx, ry in resources:
            myd = cheb(mx, my, rx, ry)
            opd = cheb(ex, ey, rx, ry)
            lead = opd - myd  # positive means I'm closer than opponent
            if lead > best or (lead == best and myd < best_tie):
                best, best_tie = lead, myd
        return best * 1000 - best_t