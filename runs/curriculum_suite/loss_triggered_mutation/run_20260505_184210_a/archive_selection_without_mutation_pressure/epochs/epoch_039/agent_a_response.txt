def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in legal:
            v = cheb(sx + dx, sy + dy, cx, cy)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = None
    bestv = None
    # Stronger role: deny the opponent. Prefer moves that reduce their advantage
    # and, if possible, create a lead toward high-value (closest) resources.
    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy
        local = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Big positive if we can beat them or swing the gap.
            gap = do - ds
            # Weight by how contested the resource is (small do).
            contest = 1.0 / (1 + do)
            # Also slightly reward general progress (smaller ds).
            local += (gap * 10.0) * contest - (ds * 0.05) + (gap > 0) * (2.5 * contest)
        # Deterministic tie-break: higher score, then closer to nearest resource.
        if bestv is None or local > bestv:
            bestv = local
            best = (dx, dy)
        elif local == bestv:
            # secondary tie-break
            def mindist(cell):
                x, y = cell
                md = None
                for rx, ry in resources:
                    v = cheb(x, y, rx, ry)
                    if md is None or v < md:
                        md = v
                return md
            if mindist((nx, ny)) < mindist((sx + best[0], sy + best[1])):
                best = (dx, dy)

    return [best[0], best[1]]