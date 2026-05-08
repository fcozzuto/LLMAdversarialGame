def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_unclaimed(x, y):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    un_list = list(unclaimed)
    def best_unclaimed_dist(x, y):
        if not un_list:
            return 10**9
        md = 10**9
        for (ux, uy) in un_list:
            d = abs(ux - x) + abs(uy - y)
            if d < md:
                md = d
        return md

    opp_bias = abs(ox - sx) + abs(oy - sy)
    best_move = dirs[0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_un = best_unclaimed_dist(nx, ny)
        score = 0
        score += 50 * adj_unclaimed(nx, ny)
        score += -2 * d_un
        if (nx, ny) in unclaimed:
            score += 80
        # Prefer moves that keep some distance from opponent when unclaimed is scarce
        score += (-1) * max(0, (abs(ox - nx) + abs(oy - ny) - opp_bias))
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]