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

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    res = set(map(tuple, observation.get("resources") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x, y, a, b):
        dx = x - a
        if dx < 0:
            dx = -dx
        dy = y - b
        if dy < 0:
            dy = -dy
        return dx + dy

    best = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = manh(nx, ny, ox, oy)
        d_opct = 0
        if d_opp == 0:
            d_opct = -400
        elif d_opp <= 2:
            d_opct = -80 * (3 - d_opp)
        elif d_opp <= 4:
            d_opct = -20 * (5 - d_opp)

        gain = 0
        if (nx, ny) in self_terr:
            gain += 2
        if (nx, ny) in unclaimed:
            gain += 10 + 2 * (observation.get("remaining_resource_count") or 0) * 0
        if (nx, ny) in res:
            gain += 7

        if (nx, ny) in op_terr:
            gain -= 25

        # Prefer staying closer to resources/unclaimed indirectly by maximizing (gain - distance)
        score = gain + d_opct + (d_opp * 1)
        if score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]