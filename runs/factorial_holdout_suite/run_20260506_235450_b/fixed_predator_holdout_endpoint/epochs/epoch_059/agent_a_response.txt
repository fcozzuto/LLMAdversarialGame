def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def clamp(x, y):
        if x < 0:
            x = 0
        elif x >= w:
            x = w - 1
        if y < 0:
            y = 0
        elif y >= h:
            y = h - 1
        return x, y

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Evaluate next move by how strongly it improves our "win potential" on the best available resource.
    # win_potential = (opp_dist - self_dist) ; higher is better. Also add small tie-break favoring shorter self_dist.
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = clamp(nx, ny)
        if (nx, ny) in obstacles:
            continue

        # Consider only a few top candidate resources to keep it cheap/deterministic.
        scored = []
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            scored.append((od - sd, -sd, rx, ry))
        # Take best 3 by win_potential then closeness (encoded by -sd).
        scored.sort(reverse=True)
        top = scored[:3]

        # Primary: max win potential we can achieve; Secondary: improved max; Tertiary: prevent opponent by considering worst-case among top.
        max_win = top[0][0]
        min_self = -top[0][1]  # actual sd
        worst_opp_adv = min((t[0] for t in top))  # lower means opponent advantage; keep it high (closer to best)

        # Combined key: maximize max_win, then maximize worst_opp_adv, then minimize min_self.
        key = (max_win, worst_opp_adv, -min_self, -dx, -dy)
        if best is None or key > best_key:
            best = (dx, dy)
            best_key = key

    if best is None:
        # If all moves blocked, stay.
        return [0, 0]
    return [int(best[0]), int(best[1])]