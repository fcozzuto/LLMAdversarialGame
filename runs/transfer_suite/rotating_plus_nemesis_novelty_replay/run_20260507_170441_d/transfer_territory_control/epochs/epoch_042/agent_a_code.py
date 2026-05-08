def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def cell_score(nx, ny):
        if not valid(nx, ny):
            return -10**9
        # Prefer stealing by moving onto opponent-controlled cells.
        s = 0
        if (nx, ny) in opp_t:
            s += 500
        # Otherwise, contest unclaimed near opponent (interceptor/denier rather than claimer).
        if (nx, ny) in unclaimed:
            dpo = abs(nx - ox) + abs(ny - oy)
            s += 120 - 5 * dpo
        # Avoid walking deeper into our own territory if opponent is close (breakout instead).
        if (nx, ny) in self_t:
            s -= 40
        # Keep moving generally towards opponent to threaten their expansion corridor.
        s += 15 - 3 * (abs(nx - ox) + abs(ny - oy))
        # Slightly prefer reducing distance to the best "threat line": toward opponent.
        s += 2 * (1 if (nx - sx) * (ox - sx) >= 0 else 0) + 1 * (1 if (ny - sy) * (oy - sy) >= 0 else 0)
        return s

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        v = cell_score(nx, ny)
        # If no direct threat, prefer steps that move closer to the nearest unclaimed to opponent.
        if v <= -10**8:
            v = 0
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]