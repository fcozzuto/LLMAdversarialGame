def choose_move(observation):
    ax, ay = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 0), observation.get("grid_height", 0)
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = {(x, y) for x, y in obstacles if inb(x, y)}
    un = {(x, y) for x, y in unclaimed if inb(x, y)}
    my = {(x, y) for x, y in my_t if inb(x, y)}
    op = {(x, y) for x, y in op_t if inb(x, y)}

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_val = -10**18

    def adj4_count(x, y, s):
        c = 0
        if inb(x + 1, y) and (x + 1, y) in s: c += 1
        if inb(x - 1, y) and (x - 1, y) in s: c += 1
        if inb(x, y + 1) and (x, y + 1) in s: c += 1
        if inb(x, y - 1) and (x, y - 1) in s: c += 1
        return c

    curd = abs(ax - ox) + abs(ay - oy)
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) in op:
            val = -10**12
        else:
            d = abs(nx - ox) + abs(ny - oy)
            dm = d - curd
            val = 0
            if (nx, ny) in my:
                val += 3 + 2 * adj4_count(nx, ny, my)
            if (nx, ny) in un:
                val += 50 + 3 * adj4_count(nx, ny, my)
                if adj4_count(nx, ny, op) > 0:
                    val -= 40
                if dm < 0:
                    val -= 12
            else:
                val += 1 * adj4_count(nx, ny, my)
                if adj4_count(nx, ny, un) > 0:
                    val += 2
                if adj4_count(nx, ny, op) > 0:
                    val -= 10
                if dm < 0:
                    val -= 5
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]