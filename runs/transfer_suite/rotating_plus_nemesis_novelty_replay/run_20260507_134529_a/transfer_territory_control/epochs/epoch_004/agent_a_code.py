def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        pts = observation.get(key, None) or []
        out = set()
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.add((int(p[0]), int(p[1])))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    resources = to_set("resources")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    un_list = list(unclaimed)
    best = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in unclaimed:
            val += 5
        if (nx, ny) in resources:
            val += 3
        # Prefer expanding/pressing near our territory
        if self_terr:
            for tx, ty in self_terr:
                if max(abs(nx - tx), abs(ny - ty)) == 1:
                    val += 1
                    break
        # Avoid getting too close to opponent
        if max(abs(nx - ox), abs(ny - oy)) <= 1:
            val -= 8
        # Greedy toward nearest unclaimed (sample limited)
        if un_list:
            lim = un_list[:50]
            md = 10**9
            for ux, uy in lim:
                d = abs(nx - ux) + abs(ny - uy)
                if d < md:
                    md = d
            val += 12 - md if md < 10**9 else 0
        if val > best[1] or (val == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), val)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]