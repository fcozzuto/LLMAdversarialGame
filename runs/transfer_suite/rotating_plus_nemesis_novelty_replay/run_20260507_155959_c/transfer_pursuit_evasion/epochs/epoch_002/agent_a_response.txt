def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if pursuer:
        best = (-10**18, None)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            # Prefer closer; tie-break toward smaller move lexicographic (deterministic)
            score = -d
            if score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return list(best[1] if best[1] is not None else (0, 0))

    # Evader: choose farthest corner, but with local "wall-run" feel via obstacle-aware scoring.
    target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    tx, ty = target
    best = (-10**18, None)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dopp = dist2(nx, ny, ox, oy)
        # Encourage moving roughly away from pursuer and toward target
        man_to = abs(nx - tx) + abs(ny - ty)
        man_away = abs(nx - ox) + abs(ny - oy)
        # Small penalty for being "corner-stuck" by obstacles
        adj_block = 0
        for ddx, ddy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            ax, ay = nx + ddx, ny + ddy
            if (not inb(ax, ay)) or ((ax, ay) in obstacles):
                adj_block += 1
        score = (dopp * 3) + (man_away * 1.0) - (man_to * 0.6) - (adj_block * 0.2)
        if score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    return list(best[1] if best[1] is not None else (0, 0))