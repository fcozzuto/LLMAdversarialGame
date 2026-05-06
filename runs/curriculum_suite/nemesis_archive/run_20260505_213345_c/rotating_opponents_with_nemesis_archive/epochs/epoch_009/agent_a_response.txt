def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Focus: choose move that maximizes our arrival advantage to the best contested resource.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_adv = None
        best_our = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our = dist2(nx, ny, rx, ry)
            opp = dist2(ox, oy, rx, ry)
            adv = opp - our  # larger => we are closer than opponent for this resource
            if best_adv is None or adv > best_adv or (adv == best_adv and our < best_our):
                best_adv = adv
                best_our = our
        # If all were blocked somehow, fallback
        if best_adv is None:
            score = (-10**9, 10**9)
        else:
            # Tie-break: also prefer moving in the general direction of the chosen resource
            score = (best_adv, -best_our)
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move