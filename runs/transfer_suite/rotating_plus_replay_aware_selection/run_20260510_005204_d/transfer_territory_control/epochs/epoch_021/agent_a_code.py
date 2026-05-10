def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass
    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.append((int(p[0]), int(p[1])))
        except:
            pass
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if unclaimed:
            d = min(dist2(nx, ny, ux, uy) for ux, uy in unclaimed)
            score = -d + 3 * (1 if (nx, ny) in unclaimed else 0)
        else:
            d = dist2(nx, ny, ox, oy)
            score = -d
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is not None:
        return best
    return [0, 0]