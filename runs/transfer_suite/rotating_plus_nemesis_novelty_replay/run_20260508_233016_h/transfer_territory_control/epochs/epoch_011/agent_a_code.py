def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = observation["opponent_position"]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def manh(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    best = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep us; keep scoring consistent

        cell = (nx, ny)
        if cell in opp_terr:
            val = 1000 - manh(nx, ny, ox, oy)  # flip territory pressure
        elif cell in unclaimed:
            val = 120 - manh(nx, ny, ox, oy)  # expand into empty
        elif cell in self_terr:
            val = 0 - manh(nx, ny, ox, oy)  # reposition without gain
        else:
            val = -50 - manh(nx, ny, ox, oy)  # likely blocked/out of interest

        # Prefer moves that get closer to the opponent position in general
        if cell not in opp_terr:
            val -= 2 * manh(nx, ny, ox, oy)

        # Small bias toward advancing toward opponent half to break symmetry
        val += 3 * (1 if nx > sx else (-1 if nx < sx else 0)) + 1 * (1 if ny > sy else (-1 if ny < sy else 0))

        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]