def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        pts = observation.get(key) or []
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    my_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_cells = list(opp_terr)[:24]
    unk_cells = list(unclaimed)[:24]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in my_terr:
            val += 2
        if (nx, ny) in opp_terr:
            val += 18
        if (nx, ny) in unclaimed:
            val += 6
        if (nx, ny) in resources:
            val += 10

        d_op = abs(nx - ox) + abs(ny - oy)
        val += -d_op * 1.0

        if unk_cells:
            du = 10**9
            for x, y in unk_cells:
                du = min(du, abs(nx - x) + abs(ny - y))
            val += max(0, 6 - 0.8 * du)
        if opp_cells:
            dt = 10**9
            for x, y in opp_cells:
                dt = min(dt, abs(nx - x) + abs(ny - y))
            val += max(0, 8 - 0.9 * dt)

        # Safety: avoid stepping adjacent to obstacles/opponent when not capturing
        adj_opp = max(abs(nx - ox), abs(ny - oy)) <= 1 and (nx, ny) not in opp_terr
        if adj_opp:
            val -= 3

        if (nx, ny) not in opp_terr:
            for ax, ay in ((nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1)):
                if inb(ax, ay) and (ax, ay) in obstacles:
                    val -= 0.6

        # Deterministic tie-breaker: prefer staying if equal, else smaller dx/dy lexicographically
        if val > best_val or (val == best_val and ((dx, dy) < best_move)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]