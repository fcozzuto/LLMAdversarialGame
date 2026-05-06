def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = w // 2, h // 2

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            key = (md(nx, ny, cx, cy), md(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Pick a resource where we can be closer than the opponent; otherwise, reduce opponent advantage.
        best_adv = None
        best_self = None
        best_opp = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            if not (0 <= rx < w and 0 <= ry < h):
                continue
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd  # positive is good for us

            if best_adv is None or adv > best_adv or (adv == best_adv and sd < best_self) or (adv == best_adv and sd == best_self and od > best_opp):
                best_adv = adv
                best_self = sd
                best_opp = od

        # Primary: maximize advantage; Secondary: if no positive advantage, prefer moving to resources with best combined pressure.
        # Tertiary: slight center bias to prevent stalemates.
        if best_adv is None:
            key = (0, 0, md(nx, ny, cx, cy), md(nx, ny, ox, oy))
        else:
            # Ensure deterministic ordering even with ties
            key = (-best_adv, best_self, -best_opp, md(nx, ny, cx, cy), md(nx, ny, ox, oy))

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]