def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    yield (nx, ny)

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in unclaimed:
            val = 1200
        elif (nx, ny) in op_terr:
            val = 650
        else:
            val = 40

        # Make moves that convert/expand locally: prefer cells surrounded by unclaimed or enemy.
        neigh_un = 0
        neigh_op = 0
        neigh_my = 0
        for px, py in neighbors(nx, ny):
            if (px, py) in unclaimed:
                neigh_un += 1
            elif (px, py) in op_terr:
                neigh_op += 1
            elif (px, py) in my_terr:
                neigh_my += 1

        val += neigh_un * 70 + neigh_op * 55 + neigh_my * 10

        # Avoid immediate tactical traps: if we step onto enemy and we're not far from enemy territory edge, be cautious.
        if (nx, ny) in op_terr:
            dist_to_op = abs(nx - ox) + abs(ny - oy)
            val += (18 if dist_to_op <= 2 else 0) - (80 if dist_to_op == 0 else 0)

        # Prefer increasing control tempo: move toward unclaimed when ahead is needed; toward opponent when behind.
        ahead = observation.get("self_territory_count", 0) - observation.get("opponent_territory_count", 0)
        d_un = min((abs(nx - ux) + abs(ny - uy) for ux, uy in unclaimed), default=20)
        d_op = abs(nx - ox) + abs(ny - oy)
        if ahead >= 0:
            val -= d_un * 2
            val += (8 - d_op) * 0.5
        else:
            val -= d_op * 3
            val += (8 - d_un) * 0.3

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]