def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx = x - cx
        dy = y - cy
        return dx * dx + dy * dy

    prevd = dist2(sx, sy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0.0
        if (nx, ny) in selfT:
            val += 1.5
        if (nx, ny) in uncla:
            val += 8.0 - 0.08 * dist2(nx, ny)
        if (nx, ny) in oppT:
            val += 22.0 - 0.02 * dist2(nx, ny)

        nd = dist2(nx, ny)
        val += 3.5 * max(0.0, prevd - nd)

        # Push into center and toward contested border: prioritize moves closer to opp territory cells
        if oppT:
            md = 10**9
            for tx, ty in oppT:
                d = abs(tx - nx) + abs(ty - ny)
                if d < md:
                    md = d
                    if md == 0:
                        break
            val += 4.0 / (1.0 + md)

        # Deterministic tie-break: prefer smaller dx, then dy
        key = (val, -abs(dx), -abs(dy), -dx, -dy)
        if key > (best[0], 0, 0, 0, 0):
            best = (key[0], dx, dy)

    dx, dy = best[1], best[2]
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]