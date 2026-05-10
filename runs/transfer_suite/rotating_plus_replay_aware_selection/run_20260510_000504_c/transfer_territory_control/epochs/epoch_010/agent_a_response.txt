def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Focus: nearest few unclaimed cells
    unclaimed_sorted = sorted(unclaimed, key=lambda p: (manh(sx, sy, p[0], p[1]), p[0], p[1]))
    samples = unclaimed_sorted[:12]

    def cell_value(t):
        if t in opp_terr:
            return 6.0
        if t in unclaimed_set:
            return 3.0
        if t in self_terr:
            return 0.5
        return 0.0

    unclaimed_set = set(unclaimed)

    best_dx, best_dy = 0, 0
    bestv = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
                dx, dy = 0, 0

            t = (nx, ny)
            v = cell_value(t)

            if samples:
                mind = None
                for ux, uy in samples:
                    d = manh(nx, ny, ux, uy)
                    if mind is None or d < mind:
                        mind = d
                v += 2.5 / (1 + mind)

            # Contention control: prefer increasing distance from opponent if not capturing immediately
            if t not in opp_terr:
                v += 0.15 * manh(nx, ny, ox, oy)

            # Mild preference for staying within claimed territory to avoid accidental contest loss
            if t not in self_terr and t not in unclaimed_set and t not in opp_terr:
                v -= 0.2

            if v > bestv or (v == bestv and (dx, dy) < (best_dx, best_dy)):
                bestv = v
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]