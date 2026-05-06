def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def best_move():
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            best = None
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    nx, ny = sx, sy
                val = -man(nx, ny, cx, cy) - 0.15 * man(nx, ny, ox, oy)
                key = (int(-val * 1000), dx, dy)
                if best is None or key < best:
                    best = key
            return [best[1], best[2]]

        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy

            our_s = 10**9
            opp_s = 10**9
            margin = -10**9
            for rx, ry in resources:
                our_d = man(nx, ny, rx, ry)
                opp_d = man(ox, oy, rx, ry)
                # contest: prefer being closer (opp_d - our_d)
                if opp_d - our_d > margin:
                    margin = opp_d - our_d
                if our_d < our_s: our_s = our_d
                if opp_d < opp_s: opp_s = opp_d

            # Prefer positions that swing contest margin; tie-break by shorter own distance, then safer distance from opponent.
            key = (-margin, our_s, -opp_s, man(nx, ny, ox, oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
        return [best_key[4], best_key[5]]

    return best_move()