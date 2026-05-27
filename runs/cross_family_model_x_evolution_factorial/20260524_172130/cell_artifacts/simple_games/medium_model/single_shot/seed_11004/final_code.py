def choose_move(observation):
    grid_w = observation.get('grid_width', 0)
    grid_h = observation.get('grid_height', 0)
    self_pos = observation.get('self_position', (0, 0))
    opp_pos = observation.get('opponent_position', (0, 0))
    x, y = self_pos if isinstance(self_pos, (list, tuple)) and len(self_pos) >= 2 else (0, 0)
    ox, oy = opp_pos if isinstance(opp_pos, (list, tuple)) and len(opp_pos) >= 2 else (0, 0)

    resources = observation.get('resources', [])
    obstacles = observation.get('obstacles', [])
    remaining = observation.get('remaining_resource_count', 0)
    self_path = observation.get('self_path', [])
    opp_path = observation.get('opponent_path', [])
    scores = observation.get('scores', {})

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    best = None
    bestd = 10**9

    # If there is any resource, move toward the nearest
    if isinstance(resources, list) and resources:
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[:2]
            elif isinstance(r, dict):
                rx = r.get('x', 0)
                ry = r.get('y', 0)
            else:
                continue
            d = abs(rx - x) + abs(ry - y)
            if d < bestd:
                bestd = d
                best = (rx - x, ry - y)

    # Avoid obstacles adjacent by preferring stay or slight deviation
    adj = [(1,0),(-1,0),(0,1),(0,-1),(0,0)]
    # If best move would go into obstacle or off-grid, pick a safe adjacent
    def safe_move(dx, dy):
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_w and 0 <= ny < grid_h:
            if isinstance(obstacles, list):
                for o in obstacles:
                    ox2 = o[0] if isinstance(o, (list, tuple)) and len(o) >= 1 else None
                    oy2 = o[1] if isinstance(o, (list, tuple)) and len(o) >= 2 else None
                    if ox2 is None:
                        continue
                    if nx == ox2 and ny == oy2:
                        return None
            return (dx, dy)
        return None

    move = (0, 0)
    if best is not None:
        dx, dy = best
        m = safe_move(int((dx > 0) - (dx < 0)), int((dy > 0) - (dy < 0)))
        if m is not None:
            move = m
        else:
            move = (0, 0)
    else:
        # No resource target, chase opponent if far, else stay
        if dist((x, y), (ox, oy)) > 1:
            move = (0, 0)
            if ox > x:
                move = (1, 0)
            elif ox < x:
                move = (-1, 0)
            elif oy > y:
                move = (0, 1)
            elif oy < y:
                move = (0, -1)
        else:
            move = (0, 0)

    dx, dy = move
    # clamp and ensure in -1..1
    dx = -1 if dx < -1 else (1 if dx > 1 else dx)
    dy = -1 if dy < -1 else (1 if dy > 1 else dy)
    return [dx, dy]
