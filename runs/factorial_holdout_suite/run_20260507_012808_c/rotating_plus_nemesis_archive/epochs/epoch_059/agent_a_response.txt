def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        # If no visible resources, head to the most distant-from-opponent corner deterministically.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        best = None
        best_d = -1
        for cx, cy in corners:
            d = cheb(cx, cy, ox, oy)
            if d > best_d:
                best_d = d
                best = (cx, cy)
        tx, ty = best
        # Move one step toward target (diagonal allowed), avoiding obstacles if possible.
        best_move = [0, 0]
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs: continue
            score = -cheb(nx, ny, tx, ty)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    best_move = [0, 0]
    best_val = -10**18

    # Evaluate each candidate next cell: prefer resources we can reach no later than opponent.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        # Slightly prefer moves that reduce distance overall and also increase denial pressure.
        for (rx, ry) in resources:
            d_us = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Win-the-resource bonus if we can arrive <= opponent.
            if d_us <= d_opp:
                val += 1200 - 120 * d_us
                # Extra denial: closer to making opponent lose contested resources.
                val += 20 * (d_opp - d_us)
            else:
                # If opponent can reach first, still value reducing their lead a bit.
                val -= 200 + 80 * (d_us - d_opp)

        # If resources remain, also add a small bias toward decreasing our distance to the closest resource.
        closest_us = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
        val += 5 * (20 - closest_us)

        if val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return best_move