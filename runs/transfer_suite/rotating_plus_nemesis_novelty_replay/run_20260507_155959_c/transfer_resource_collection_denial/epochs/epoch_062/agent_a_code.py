def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_next = (sx, sy)
    best_val = None

    valid_next = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            valid_next.append((nx, ny))

    if not valid_next:
        return [0, 0]

    if not resources:
        cx, cy = w // 2, h // 2
        for nx, ny in valid_next:
            val = -md(nx, ny, cx, cy)
            if best_val is None or val > best_val or (val == best_val and (nx, ny) < best_next):
                best_val = val
                best_next = (nx, ny)
        return [best_next[0] - sx, best_next[1] - sy]

    # Evaluate each candidate next cell by the best "resource race" advantage it offers.
    for nx, ny in valid_next:
        self_next_dist = None
        # Find maximum advantage among resources for this next position.
        # Advantage: (opponent_dist - self_dist), tie-break: smaller self_dist, then lexicographic resource.
        best_adv = None
        best_sd = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_sd is None or sd < best_sd)) or (adv == best_adv and sd == best_sd and (rx, ry) < self_next_dist):
                best_adv = adv
                best_sd = sd
                self_next_dist = (rx, ry)
        # Extra preference: if this cell is itself a resource, strongly prefer.
        on_resource = 1 if any(nx == rx and ny == ry for rx, ry in resources) else 0
        val = (on_resource * 1000000) + (best_adv * 1000) - (best_sd if best_sd is not None else 0)
        if best_val is None or val > best_val or (val == best_val and (nx, ny) < best_next):
            best_val = val
            best_next = (nx, ny)

    return [best_next[0] - sx, best_next[1] - sy]