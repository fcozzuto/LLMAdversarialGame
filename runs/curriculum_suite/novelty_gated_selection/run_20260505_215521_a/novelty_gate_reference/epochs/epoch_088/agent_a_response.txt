def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def self_dist(x, y): return abs(x - sx) + abs(y - sy)
    def opp_dist(x, y): return abs(x - ox) + abs(y - oy)

    def resource_priority(x, y):
        sd = self_dist(x, y)
        od = opp_dist(x, y)
        # Compete: prefer cells where we are closer than opponent (large advantage).
        # If tie, prefer overall closeness and then stable parity.
        return (od - sd, -sd, (x + y) % 2, x, y)

    # Evaluate best outcome after our one-step move: choose the move with highest achievable priority.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; mirror deterministically
        # Compute priority from this hypothetical position by redefining distance terms.
        # Advantage uses (opp_d - self_d) where self_d is from (nx,ny).
        def sd(c1, c2): return abs(c1 - nx) + abs(c2 - ny)
        def od(c1, c2): return abs(c1 - ox) + abs(c2 - oy)

        chosen = None
        chosen_val = None
        for rx, ry in resources:
            adv = od(rx, ry) - sd(rx, ry)
            val = (adv, -sd(rx, ry), (rx + ry) % 2, rx, ry)
            if chosen_val is None or val > chosen_val:
                chosen_val = val
                chosen = (rx, ry)

        if best_val is None or chosen_val > best_val:
            best_val = chosen_val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]