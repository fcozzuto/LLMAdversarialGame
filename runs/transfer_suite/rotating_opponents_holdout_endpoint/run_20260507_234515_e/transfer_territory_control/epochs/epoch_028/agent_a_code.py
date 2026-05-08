def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    resources = []
    for p in observation.get("resources") or []:
        try:
            x, y = p
            resources.append((int(x), int(y)))
        except:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        opp_dist = man(nx, ny, ox, oy)
        score = 0
        if resources:
            score = -min(man(nx, ny, rx, ry) for rx, ry in resources)
        else:
            score = -man(nx, ny, ox, oy)
        score += opp_dist  # prefer being farther from opponent
        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]